"""Build section embeddings and source-grounded notes using local Ollama only."""

from datetime import datetime
import json
import re
from time import perf_counter

import numpy as np
import ollama

from . import config
from .wiki_plan import NOTE_PLAN

# Structured output keeps formatting and citations in simple, inspectable Python.
SOURCE_IDS = {"type": "array", "items": {"type": "string"}, "minItems": 1}
NOTE_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 3},
        "summary_sources": SOURCE_IDS,
        "key_points": {"type": "array", "minItems": 1, "items": {
            "type": "object", "properties": {
                "text": {"type": "string"}, "sources": SOURCE_IDS,
            }, "required": ["text", "sources"], "additionalProperties": False,
        }},
        "related_notes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "summary_sources", "key_points", "related_notes"],
    "additionalProperties": False,
}


def read_chunks(raw_dir):
    """Read every Markdown file; ignore the preamble before its first ## heading."""
    chunks = []
    for path in sorted(raw_dir.rglob("*.md")):
        text = path.read_text(encoding="utf-8-sig")
        # Ignore heading-looking lines inside fenced code blocks.
        sections = []
        fence = None
        for line in text.splitlines():
            marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
            if marker:
                token = marker.group(1)
                if fence is None:
                    fence = token
                elif token[0] == fence[0] and len(token) >= len(fence):
                    fence = None
            if fence is None and line.startswith("## "):
                sections.append([line[3:].strip(), []])
            elif sections:
                sections[-1][1].append(line)
        if not sections:
            raise ValueError(f"{path.name}: no ## sections found")
        seen = set()
        for position, (heading, lines) in enumerate(sections, 1):
            match = re.match(r"^(\d+)[.)]?\s", heading)
            number = int(match.group(1)) if match else position
            if number in seen:
                raise ValueError(f"{path.name}: duplicate section number {number}")
            seen.add(number)
            source = path.relative_to(raw_dir).as_posix()
            chunks.append({"id": f"{source}::{number}", "source_file": source,
                           "section_number": number, "section_heading": heading,
                           "text": "\n".join(lines).strip()})
    if not chunks:
        raise ValueError("No Markdown sources found in vault/raw")
    return chunks


def clean_links(text, approved):
    """Remove unapproved link syntax, keeping the readable label and an audit list."""
    removed = []
    def replace(match):
        link = match.group(1)
        if link in approved:
            return match.group(0)
        removed.append(match.group(0))
        return link.split("|", 1)[-1]
    return re.sub(r"\[\[([^\[\]\n]+)\]\]", replace, text), removed



def clean_related_notes(names, title):
    """Keep first occurrences in order and report every self-link or duplicate."""
    kept = []
    seen = set()
    removed = []
    for name in names:
        name = name.strip()
        if name == title:
            removed.append(f"[[{name}]] (self-link)")
        elif name in seen:
            removed.append(f"[[{name}]] (duplicate)")
        else:
            kept.append(name)
            seen.add(name)
    return kept, removed


def render_note(note, folder, title, sections, created):
    """Validate source IDs, then render YAML and citations without a YAML dependency."""
    by_id = {section["id"]: section for section in sections}
    used = set()
    def references(ids):
        if not ids or any(source_id not in by_id for source_id in ids):
            raise ValueError("Model returned missing or unapproved source IDs")
        used.update(ids)
        return " ".join(
            f"(source: {by_id[source_id]['source_file']}, section {by_id[source_id]['section_number']})"
            for source_id in dict.fromkeys(ids)
        )
    # Track the summary's evidence in the frontmatter, even without inline citations.
    references(note["summary_sources"])
    sentences = note["summary"]
    if not isinstance(sentences, list) or not 2 <= len(sentences) <= 3:
        raise ValueError("Summary must contain two or three sentence strings")
    summary = " ".join(sentence.strip() for sentence in sentences)
    if not summary or not note["key_points"]:
        raise ValueError("Model returned an empty summary or key points")
    body = [summary, "", "## Key points", ""]
    for point in note["key_points"]:
        text = " ".join(point["text"].split())
        if not text:
            raise ValueError("Model returned an empty key point")
        body.append(f"- {text} {references(point['sources'])}")
    body.extend(["", "## Related notes", ""])
    body.extend(f"- [[{name}]]" for name in note["related_notes"])
    # JSON double-quoted strings are valid YAML scalars, including escaped quotes.
    quote = lambda value: json.dumps(value, ensure_ascii=False)
    header = ["---", f"title: {quote(title)}", f"folder: {quote(folder)}", "sources:"]
    for section in sections:
        if section["id"] in used:
            header.append("  - " + quote(f"{section['source_file']}, section {section['section_heading']}"))
    header.extend([f"created: {created}", "---", ""])
    return "\n".join(header + body) + "\n"


def write_index():
    """Deterministic index descriptions come from the approved plan, not extra model calls."""
    lines = ["# Personal Wiki", "", "Study Project Management using source-grounded class notes.", ""]
    for folder in ("Concepts", "Selection", "Initiation", "Cases"):
        lines.extend([f"## {folder}", ""])
        for category, title, description, _ in NOTE_PLAN:
            if category == folder and (config.WIKI_DIR / folder / f"{title}.md").exists():
                lines.append(f"- [[{title}]] — {description}")
        lines.append("")
    config.INDEX_PATH.write_text("\n".join(lines), encoding="utf-8")


def save_embeddings(chunks, client, record=print):
    """Write only data/: row i is the embedding of chunks[i], with retrieval prompts."""
    vectors = []
    for index, chunk in enumerate(chunks, 1):
        record(f"Embedding {index}/{len(chunks)}: {chunk['source_file']}, section {chunk['section_number']}")
        result = client.embed(model=config.EMBEDDING_MODEL,
                              input=config.EMBEDDING_DOCUMENT_FORMAT.format(
                                  title=chunk["section_heading"], content=chunk["text"]),
                              truncate=False)
        vectors.append(result.embeddings[0])
    embeddings = np.asarray(vectors, dtype=np.float32)
    if embeddings.ndim != 2 or not np.isfinite(embeddings).all() or np.any(np.linalg.norm(embeddings, axis=1) == 0):
        raise ValueError("Invalid embedding vectors returned by Ollama")
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    # Row i in embeddings.npy corresponds to item i in chunks.json.
    np.save(config.DATA_DIR / "embeddings.npy", embeddings, allow_pickle=False)
    payload = {"embedding_model": config.EMBEDDING_MODEL, "created": datetime.now().astimezone().isoformat(),
               "document_format": config.EMBEDDING_DOCUMENT_FORMAT, "chunks": chunks}
    (config.DATA_DIR / "chunks.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    record(f"Saved {len(chunks)} chunks and embeddings with shape {embeddings.shape}.")


def rebuild_embeddings():
    """Rebuild retrieval data without reading prompts or writing any vault file."""
    started = perf_counter()
    try:
        chunks = read_chunks(config.RAW_DIR)
        client = ollama.Client(host=config.OLLAMA_HOST,
                               timeout=config.INGEST_TIMEOUT_SECONDS, trust_env=False)
        save_embeddings(chunks, client, lambda message: print(message, flush=True))
        print(f"Embedding rebuild time: {perf_counter() - started:.2f} seconds.")
        return 0
    except Exception as error:
        print(f"Error rebuilding embeddings: {error}. Check local Ollama and embeddinggemma.")
        return 1


def ingest(force=False):
    """One generation per new note; failures are logged and manual edits are preserved."""
    started = perf_counter()
    now = datetime.now().astimezone()
    config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = config.OUTPUTS_DIR / "ingest-log.md"
    log = ["# Ingest log", "", f"Date: {now.isoformat(timespec='seconds')}",
           f"Generation model: {config.GENERATION_MODEL}",
           f"Embedding model: {config.EMBEDDING_MODEL}", f"Force: {force}", ""]
    errors = []
    def record(message):
        print(message, flush=True)
        log.append(message)
        log_path.write_text("\n\n".join(log) + "\n", encoding="utf-8")
    try:
        chunks = read_chunks(config.RAW_DIR)
        by_key = {(c["source_file"], c["section_number"]): c for c in chunks}
        # Validate every mapping before spending time on embeddings or generation.
        selections = []
        for folder, title, description, mapping in NOTE_PLAN:
            selections.append([by_key[(source, number)] for source, numbers in mapping for number in numbers])
        instructions = (config.PROMPTS_DIR / "wiki-instructions.md").read_text(encoding="utf-8")
        client = ollama.Client(host=config.OLLAMA_HOST, timeout=config.INGEST_TIMEOUT_SECONDS, trust_env=False)
        installed = {m.model for m in client.list().models}
        for model in (config.EMBEDDING_MODEL, config.GENERATION_MODEL):
            name = model if ":" in model else model + ":latest"
            if name not in installed:
                raise ValueError(f"Missing local model {model}; install it before running offline")
        save_embeddings(chunks, client, record)
        # Unload embeddings before loading Gemma on this 16 GB laptop.
        client.embed(model=config.EMBEDDING_MODEL, input="", keep_alive=0)
        approved = {entry[1] for entry in NOTE_PLAN}
        for index, ((folder, title, _, _), sections) in enumerate(zip(NOTE_PLAN, selections), 1):
            path = config.WIKI_DIR / folder / f"{title}.md"
            if path.exists() and not force:
                record(f"[{index}/{len(NOTE_PLAN)}] Skipped {folder}/{title}.md (existing; 0.00 seconds).")
                continue
            note_started = perf_counter()
            record(f"[{index}/{len(NOTE_PLAN)}] Generating {folder}/{title}.md ...")
            try:
                prompt = json.dumps({"title": title, "folder": folder,
                                     "approved_note_titles": sorted(approved - {title}),
                                     "source_sections": sections}, ensure_ascii=False)
                result = client.generate(model=config.GENERATION_MODEL, system=instructions,
                                         prompt=prompt, format=NOTE_SCHEMA, think=False, stream=False,
                                         options={"temperature": 0, "num_ctx": 8192, "num_predict": 1800})
                if result.done_reason == "length":
                    raise ValueError("Generation hit token limit; note was not saved")
                note = json.loads(result.response)
                # Clean only Related notes; keep an audit entry for every removal.
                note["related_notes"], removed = clean_related_notes(note["related_notes"], title)
                content = render_note(note, folder, title, sections, now.date().isoformat())
                content, unapproved = clean_links(content, approved)
                removed.extend(unapproved)
                # Exclusive creation also protects against a note created while the model ran.
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("w" if force else "x", encoding="utf-8") as handle:
                    handle.write(content)
                record(f"[{index}/{len(NOTE_PLAN)}] Saved {folder}/{title}.md — {perf_counter() - note_started:.2f} seconds; "
                       f"{len(content.split())} words including frontmatter. Links removed: {removed or 'none'}.")
            except Exception as error:
                message = f"{folder}/{title}.md: {error} ({perf_counter() - note_started:.2f} seconds)"
                errors.append(message)
                record("ERROR: " + message)
        write_index()
    except (Exception, KeyboardInterrupt) as error:
        message = str(error) or "Interrupted by user"
        errors.append(message)
        record("ERROR: " + message + ". Check local Ollama and the source files; rerun to resume.")
    finally:
        record(f"Total ingest time: {perf_counter() - started:.2f} seconds.")
        record(f"Errors: {len(errors)}" + (" — " + "; ".join(errors) if errors else " (none)."))
    return 1 if errors else 0
