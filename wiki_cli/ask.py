"""Answer using the same hybrid retrieval, with mechanical citation checks."""

from datetime import datetime
import json
import re
from time import perf_counter

import ollama

from . import config
from .search import retrieve


def check_citations(answer, passages):
    """Check numeric references only; this does not grade factual correctness."""
    occurrences = [int(number) for number in re.findall(r"\[([0-9]+)\]", answer)]
    used = list(dict.fromkeys(occurrences))  # First-use order, without duplicates.
    available = {passage["rank"]: passage for passage in passages}
    sources = []
    warnings = []
    for number in used:
        if number not in available:
            warnings.append(f"Invalid citation [{number}]: no such retrieved passage.")
        else:
            passage = available[number]
            sources.append(f"[{number}] -> vault/raw/{passage['source_file']}, "
                           f"section {passage['section_number']}: {passage['section_heading']}")
    if not used and answer != config.INSUFFICIENT_EVIDENCE:
        warnings.append("Answer has no citations and is not the exact insufficient-evidence sentence.")
    return {"occurrences": occurrences, "used": used, "sources": sources, "warnings": warnings}


def build_prompt(question, passages):
    """Label full retrieved sections; passage text and the question are untrusted data."""
    persona = (config.PROMPTS_DIR / "persona.md").read_text(encoding="utf-8")
    instructions = (config.PROMPTS_DIR / f"ask-{config.ASK_PROMPT_VERSION}.md").read_text(encoding="utf-8")
    blocks = []
    for passage in passages:
        blocks.append(f"[{passage['rank']}] Source: vault/raw/{passage['source_file']}\n"
                      f"Section {passage['section_number']}: {passage['section_heading']}\n"
                      f"{passage['text']}")
    prompt = "PASSAGES\n\n" + "\n\n".join(blocks) + "\n\nQUESTION\n" + question
    return persona + "\n\n" + instructions, prompt


def citation_text(check):
    """Shared text for the terminal, per-run record, and test summary."""
    used = ", ".join(f"[{n}]" for n in check["used"]) or "None"
    occurrences = ", ".join(f"[{n}]" for n in check["occurrences"]) or "None"
    lines = [f"Citations used: {used}", f"Citation occurrences: {occurrences}", "", "Sources", ""]
    lines.extend("- " + source for source in check["sources"])
    if not check["sources"]:
        lines.append("- None")
    lines.extend(["", "Citation warnings: " + ("; ".join(check["warnings"]) or "None")])
    return "\n".join(lines)


def timing_text(report):
    def seconds(value):
        return "not completed" if value is None else f"{value:.3f} s"
    return (f"Search: {seconds(report['search_seconds'])}; "
            f"Generation: {seconds(report['generation_seconds'])}; "
            f"Total: {seconds(report['total_seconds'])}")


def save_run(report):
    """Save every attempted run, including failures, without overwriting past evidence."""
    directory = config.OUTPUTS_DIR / "ask"
    directory.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", report["question"].lower()).strip("-")[:70] or "question"
    path = directory / (datetime.now().strftime("%Y%m%d-%H%M%S-%f") + "-" + slug + ".md")
    lines = ["# Ask run", "", f"Date: {report['date']}", f"Question: {report['question']}",
             f"Prompt version: {report['prompt_version']}",
             f"Model: {config.GENERATION_MODEL}", f"Embedding model: {config.EMBEDDING_MODEL}",
             "Settings: think=False; " + json.dumps(report["settings"]),
             f"Retrieval: top_k={config.TOP_K}; keyword={config.KEYWORD_WEIGHT}; semantic={config.SEMANTIC_WEIGHT}",
             "", "## Retrieved passages (full text)", ""]
    for passage in report["passages"]:
        lines.extend([f"### [{passage['rank']}] vault/raw/{passage['source_file']}",
                      f"Section {passage['section_number']}: {passage['section_heading']}",
                      f"Final score: {passage['final']:.6f}", "", passage["text"], ""])
    lines.extend(["## Answer", "", report["answer"], "", "## Citation check", "",
                  citation_text(report["citation_check"]), "",
                  "This check only validates reference numbers and citation presence; it does not grade claims.",
                  "", "## Timings", "", timing_text(report),
                  "Total includes retrieval, prompt construction, generation, and citation checking; excludes saving/printing.",
                  "", f"Generation done reason: {report['done_reason']}",
                  "Run warnings: " + ("; ".join(report["run_warnings"]) or "None"),
                  "Error: " + (report["error"] or "None"), "", "## System prompt", "", report["system_prompt"], ""])
    with path.open("x", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    return path


def run_ask(question):
    """Retrieve once, generate once, check citations, and always save an audit record."""
    started = perf_counter()
    report = {"date": datetime.now().astimezone().isoformat(timespec="seconds"),
              "question": question, "prompt_version": config.ASK_PROMPT_VERSION, "settings": {"temperature": config.ASK_TEMPERATURE,
                  "seed": config.ASK_SEED, "num_ctx": config.ASK_NUM_CTX, "num_predict": config.ASK_NUM_PREDICT},
              "passages": [], "answer": "", "system_prompt": "",
              "citation_check": {"occurrences": [], "used": [], "sources": [], "warnings": []},
              "search_seconds": None, "generation_seconds": None, "total_seconds": None,
              "done_reason": None, "run_warnings": [], "error": None}
    try:
        print("Searching local notes...", flush=True)
        search = retrieve(question)
        report["passages"] = search["results"]
        report["search_seconds"] = search["seconds"]
        system, prompt = build_prompt(question, report["passages"])
        report["system_prompt"] = system
        client = ollama.Client(host=config.OLLAMA_HOST, timeout=config.ASK_TIMEOUT_SECONDS, trust_env=False)
        print("Generating a local answer (thinking disabled)...", flush=True)
        generation_started = perf_counter()
        try:
            response = client.generate(model=config.GENERATION_MODEL, system=system, prompt=prompt,
                                       think=False, stream=False, options=report["settings"])
        finally:
            report["generation_seconds"] = perf_counter() - generation_started
        # Strip only surrounding whitespace; do not correct, rewrite, or grade the answer.
        report["answer"] = response.response.strip()
        report["done_reason"] = response.done_reason
        if response.done_reason == "length":
            report["run_warnings"].append("Generation reached its token limit; the answer may be incomplete.")
        report["citation_check"] = check_citations(report["answer"], report["passages"])
    except (Exception, KeyboardInterrupt) as error:
        report["error"] = str(error) or "Interrupted by user"
    report["total_seconds"] = perf_counter() - started
    report["saved_path"] = str(save_run(report))
    return report


def print_report(report):
    print("\n" + report["answer"] + "\n")
    print(citation_text(report["citation_check"]))
    for warning in report["run_warnings"]:
        print("Warning: " + warning)
    if report["error"]:
        print("Error: " + report["error"] + ". Check local Ollama, installed models, and retrieval data.")
    print("\n" + timing_text(report))
    print("Saved: " + report["saved_path"])


def ask(question):
    try:
        report = run_ask(question)
        print_report(report)
        return 1 if report["error"] else 0
    except Exception as error:
        print(f"Error saving ask run: {error}. Check write access to outputs/ask/.")
        return 1
