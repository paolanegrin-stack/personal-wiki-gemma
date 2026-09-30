"""Local chat with model routing, bounded history, and saved evidence."""

from datetime import datetime
import json
from pathlib import Path
import re
from time import perf_counter

import ollama

from . import config
from .ask import build_prompt, check_citations, citation_text
from .search import retrieve

HELP = "/quit: exit and save | /reset: clear history | /sources: last answer's sources | /help"
REWRITER = (
    "Rewrite the latest message as a standalone search query about the user's Project Management notes. "
    "Use recent history to resolve pronouns and omitted topics. Preserve the user's intent. "
    "Return only the query, without answering it, adding facts, or explaining the rewrite."
)


def parse_route(text):
    """Accept exact labels (ignoring outer whitespace); otherwise require retrieval."""
    label = text.strip()
    return label if label in ("SEARCH", "NO_SEARCH") else "SEARCH"


def recent_history(history, limit):
    """Keep complete user/assistant pairs, not individual messages."""
    if limit < 0:
        raise ValueError("History limit cannot be negative")
    return history[-limit:] if limit else []


def history_messages(history):
    messages = []
    for turn in history:
        messages.extend([{"role": "user", "content": turn["message"]},
                         {"role": "assistant", "content": turn["answer"]}])
    return messages


def timing_text(turn):
    return "; ".join(f"{name}: {value:.3f} s" for name, value in turn["timings"].items())


class ChatSession:
    """History is bounded; the transcript retains every turn and command."""
    def __init__(self):
        self.history = []
        self.previous_user = None
        self.router_version = config.ROUTER_PROMPT_VERSION
        self.turns = []
        self.events = []
        self.last_sources = []
        self.client = ollama.Client(host=config.OLLAMA_HOST, timeout=config.ASK_TIMEOUT_SECONDS, trust_env=False)
        directory = config.OUTPUTS_DIR / "chat"
        directory.mkdir(parents=True, exist_ok=True)
        self.path = directory / (datetime.now().strftime("%Y%m%d-%H%M%S-%f") + ".md")
        self.path.touch(exist_ok=False)
        self.date = datetime.now().astimezone().isoformat(timespec="seconds")
        self.save()

    def call_model(self, system, user, history, tokens, temperature):
        messages = [{"role": "system", "content": system}]
        messages.extend(history_messages(history))
        messages.append({"role": "user", "content": user})
        return self.client.chat(model=config.GENERATION_MODEL, messages=messages,
                                think=False, stream=False,
                                options={"temperature": temperature, "seed": config.ASK_SEED,
                                         "num_ctx": config.ASK_NUM_CTX, "num_predict": tokens})

    def route(self, message, history):
        """V2 sees just two user messages; assistant answers never enter routing."""
        prompt = (config.PROMPTS_DIR / f"router-{self.router_version}.md").read_text(encoding="utf-8")
        if self.router_version == "v1":
            return self.call_model(prompt, message, history, config.CHAT_ROUTE_TOKENS, 0)
        if self.router_version != "v2":
            raise ValueError("Router version must be v1 or v2")
        user = json.dumps({"previous_user_message": self.previous_user,
                           "new_user_message": message}, ensure_ascii=False)
        return self.call_model(prompt, user, [], config.CHAT_ROUTE_TOKENS, 0)

    def reset(self):
        self.history.clear()
        self.previous_user = None
        self.last_sources.clear()
        self.events.append({"command": "/reset", "after_turn": len(self.turns)})
        self.save()

    def answer(self, message):
        started = perf_counter()
        history = recent_history(self.history, config.CHAT_HISTORY_TURNS)
        turn = {"number": len(self.turns) + 1, "message": message, "history_turns": len(history),
                "router_previous_user": self.previous_user,
                "route_raw": "", "route": None, "query": None, "passages": [], "answer": "",
                "check": {"used": [], "occurrences": [], "sources": [], "warnings": []},
                "timings": {"Routing": 0., "Rewrite": 0., "Search": 0., "Generation": 0., "Total": 0.},
                "warnings": [], "error": None}
        def timed(name, action):
            begin = perf_counter()
            try:
                return action()
            finally:
                turn["timings"][name] = perf_counter() - begin
        try:
            response = timed("Routing", lambda: self.route(message, history))
            turn["route_raw"] = response.message.content or ""
            turn["route"] = parse_route(turn["route_raw"])
            if turn["route_raw"].strip() not in ("SEARCH", "NO_SEARCH"):
                turn["warnings"].append("Invalid routing output; fell back to SEARCH.")
            if turn["route"] == "SEARCH":
                rewritten = timed("Rewrite", lambda: self.call_model(REWRITER, message, history, config.CHAT_QUERY_TOKENS, 0))
                query = (rewritten.message.content or "").strip()
                if not query or rewritten.done_reason == "length":
                    query = message
                    turn["warnings"].append("Empty or truncated rewrite; used the original message as the query.")
                turn["query"] = query
                search = timed("Search", lambda: retrieve(query))
                turn["passages"] = search["results"]
                system, prompt = build_prompt(query, turn["passages"])
                system += ("\n\nRecent conversation is context for interpreting the question, not factual evidence. "
                           "Use only the current passages as evidence; citation numbers restart for each answer. "
                           "Do not reuse earlier citation numbers as identifiers for current sources.")
                print("[search: yes | query: " + json.dumps(query, ensure_ascii=False) + "]", flush=True)
            else:
                persona = (config.PROMPTS_DIR / "persona.md").read_text(encoding="utf-8")
                system = persona + ("\n\nThis is a conversational turn without retrieval. Reply briefly to greetings, "
                                    "thanks, or questions about this conversation using recent history. "
                                    "Use no citations. Do not invent or teach project management course content. "
                                    "If course facts are needed, ask for a specific question instead. "
                                    "The persona's evidence-refusal rule does not prevent greetings or thanks.")
                prompt = message
                print("[search: no]", flush=True)
            response = timed("Generation", lambda: self.call_model(system, prompt, history, config.ASK_NUM_PREDICT, config.ASK_TEMPERATURE))
            turn["answer"] = (response.message.content or "").strip()
            if response.done_reason == "length":
                turn["warnings"].append("Generation hit the token limit; answer may be incomplete.")
            if turn["route"] == "SEARCH":
                turn["check"] = check_citations(turn["answer"], turn["passages"])
            else:
                numbers = [int(n) for n in re.findall(r"\[([0-9]+)\]", turn["answer"])]
                turn["check"]["occurrences"] = numbers
                turn["check"]["used"] = list(dict.fromkeys(numbers))
                if numbers:
                    turn["check"]["warnings"].append("NO_SEARCH answer contains citations although no passages were retrieved.")
            self.last_sources = turn["check"]["sources"].copy()
            self.history = recent_history(history + [{"message": message, "answer": turn["answer"]}], config.CHAT_HISTORY_TURNS)
        except (Exception, KeyboardInterrupt) as error:
            turn["error"] = str(error) or "Interrupted by user"
            self.last_sources = []
        turn["timings"]["Total"] = perf_counter() - started
        self.previous_user = message  # Track user input even if a turn failed.
        self.turns.append(turn)
        self.save()
        print(turn["answer"])
        print(citation_text(turn["check"]))
        for warning in turn["warnings"]:
            print("Warning: " + warning)
        if turn["error"]:
            print("Error: " + turn["error"])
        print(timing_text(turn) + "\n", flush=True)
        return turn

    def save(self):
        lines = ["# Chat transcript", "", f"Date: {self.date}", f"Router prompt version: {self.router_version}",
                 f"Model: {config.GENERATION_MODEL}; embedding model: {config.EMBEDDING_MODEL}",
                 f"Search answer prompt: ask-{config.ASK_PROMPT_VERSION}; history limit: {config.CHAT_HISTORY_TURNS} complete turns",
                 f"think=False; answer temperature={config.ASK_TEMPERATURE}; seed={config.ASK_SEED}; num_ctx={config.ASK_NUM_CTX}; answer tokens={config.ASK_NUM_PREDICT}",
                 f"Routing/rewrite temperature=0; token limits={config.CHAT_ROUTE_TOKENS}/{config.CHAT_QUERY_TOKENS}",
                 "Timings include model loading; total excludes transcript saving and final output printing.", ""]
        for turn in self.turns:
            lines += [f"## Turn {turn['number']}", "", f"Message: {turn['message']}",
                      f"History turns supplied: {turn['history_turns']}",
                      f"Router previous user: {json.dumps(turn['router_previous_user'])}",
                      f"Routing output: {json.dumps(turn['route_raw'])}", f"Routing decision: {turn['route']}",
                      f"Rewritten query: {turn['query'] if turn['query'] is not None else 'Not applicable'}",
                      "", "### Retrieved passages", ""]
            for passage in turn["passages"]:
                lines += [f"[{passage['rank']}] vault/raw/{passage['source_file']}, section {passage['section_number']}: {passage['section_heading']}", "", passage["text"], ""]
            if not turn["passages"]:
                lines.append("None")
            lines += ["", "### Answer", "", turn["answer"], "", "### Citation check", "", citation_text(turn["check"]),
                      "", "### Timings", "", timing_text(turn),
                      "Run warnings: " + ("; ".join(turn["warnings"]) or "None"),
                      "Error: " + (turn["error"] or "None"), ""]
        lines += ["## Session commands", ""]
        lines += [f"- After turn {event['after_turn']}: {event['command']}" for event in self.events]
        self.path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def chat(script=None):
    session = None
    try:
        messages = iter(Path(script).read_text(encoding="utf-8-sig").splitlines()) if script else None
        session = ChatSession()
        print("Local wiki chat. " + HELP)
        while True:
            try:
                message = next(messages) if messages is not None else input("You: ")
            except (StopIteration, EOFError):
                break
            message = message.strip()
            if not message:
                continue
            if messages is not None:
                print("You: " + message, flush=True)
            if message == "/reset":
                session.reset()
                print("History cleared; previous turns remain in the saved transcript.")
            elif message.startswith("/"):
                session.events.append({"command": message, "after_turn": len(session.turns)})
                if message == "/quit":
                    break
                if message == "/sources":
                    print("\n".join(session.last_sources) or "No sources for the last answer.")
                elif message == "/help":
                    print(HELP)
                else:
                    print("Unknown command. " + HELP)
                session.save()
            else:
                turn = session.answer(message)
                if turn["error"] == "Interrupted by user":
                    break
        return 1 if any(turn["error"] for turn in session.turns) else 0
    except KeyboardInterrupt:
        print("\nSession interrupted.")
        return 0
    except Exception as error:
        print(f"Chat error: {error}. Check local Ollama, retrieval data, and file access.")
        return 1
    finally:
        if session is not None:
            session.save()
            print(f"Saved transcript: {session.path}")
