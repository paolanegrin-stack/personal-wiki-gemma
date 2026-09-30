"""Command-line harness. Help, status, ingest, search, and ask are implemented."""

import argparse
import json
import sys
from time import perf_counter
from urllib.request import ProxyHandler, build_opener

import ollama

from . import config


def model_is_installed(wanted: str, installed: set[str]) -> bool:
    """Ollama expands a model name with no tag to name:latest."""
    full_name = wanted if ":" in wanted else f"{wanted}:latest"
    return full_name in installed


def status() -> int:
    """Check the local server, check its model list, then time a short response."""
    print(f"Ollama server: {config.OLLAMA_HOST}")
    print(f"Generation model: {config.GENERATION_MODEL}")
    print(f"Embedding model: {config.EMBEDDING_MODEL}")

    # Ignore proxy environment settings: these requests must stay on localhost.
    client = ollama.Client(host=config.OLLAMA_HOST, timeout=10, trust_env=False)
    try:
        installed = {entry.model for entry in client.list().models}
        # Read the server version using Python's standard library.
        opener = build_opener(ProxyHandler({}))
        with opener.open(f"{config.OLLAMA_HOST}/api/version", timeout=10) as response:
            version = json.load(response)["version"]
        print(f"Ollama version: {version}")
    except Exception as error:
        # At this CLI boundary, report server/network errors without a traceback.
        print(
            f"Error: cannot check local Ollama at {config.OLLAMA_HOST}. "
            "Open the Ollama app or run 'ollama serve', then retry 'wiki status'.\n"
            f"Details: {error}",
            file=sys.stderr,
        )
        return 1

    missing = [
        name
        for name in (config.GENERATION_MODEL, config.EMBEDDING_MODEL)
        if not model_is_installed(name, installed)
    ]
    if missing:
        print(f"Error: missing local model(s): {', '.join(missing)}.", file=sys.stderr)
        print(
            "Install these models in Ollama before working offline, then retry. "
            "This CLI never downloads models automatically.",
            file=sys.stderr,
        )
        for name in missing:
            print(f"  One-time setup command: ollama pull {name}", file=sys.stderr)
        return 1

    print("Both models are installed.")
    print("Running a short local generation (thinking disabled)...", flush=True)
    started = perf_counter()
    try:
        client = ollama.Client(
            host=config.OLLAMA_HOST,
            timeout=config.STATUS_TIMEOUT_SECONDS,
            trust_env=False,
        )
        result = client.generate(
            model=config.GENERATION_MODEL,
            prompt="Reply with only this sentence: The local wiki is ready.",
            think=False,
            stream=False,
            options={"num_predict": 32, "num_ctx": 2048, "temperature": 0},
        )
        elapsed = perf_counter() - started
        answer = result.response.strip()
        if not answer:
            print("Error: Ollama returned an empty test response. Retry 'wiki status'.", file=sys.stderr)
            return 1
        print(f"Test response: {answer}")
        print(f"Generation time: {elapsed:.2f} seconds (includes model loading if needed)")
        return 0
    except Exception as error:
        print(
            f"Error: local generation failed after {perf_counter() - started:.2f} seconds.\n"
            "Check that Ollama is running and has enough free memory; "
            "close memory-heavy apps and retry 'wiki status'.\n"
            f"Details: {error}",
            file=sys.stderr,
        )
        return 1


def build_parser() -> argparse.ArgumentParser:
    """Describe the future commands now, without implementing their behavior."""
    parser = argparse.ArgumentParser(
        prog="wiki",
        description="Personal wiki using local Ollama models. Help, status, ingest, search, ask, and chat are available.",
        epilog=(
            'Examples: wiki status | wiki ingest | wiki search "project charter" | '
            'wiki ask "What is a project?" | wiki chat. '
            "Use wiki COMMAND --help for command-specific inputs."
        ),
    )
    commands = parser.add_subparsers(dest="command", metavar="COMMAND")
    commands.add_parser("status", help="Check local Ollama and both models; time a test response. No inputs.")
    ingest_parser = commands.add_parser("ingest", help="Build notes and embeddings from vault/raw. No required inputs.")
    ingest_options = ingest_parser.add_mutually_exclusive_group()
    ingest_options.add_argument("--embeddings-only", action="store_true", help="Rebuild only data/ embeddings and metadata; never write the vault.")
    ingest_options.add_argument("--force", action="store_true", help="Regenerate existing wiki notes, replacing manual edits.")
    search = commands.add_parser("search", help='Hybrid search of raw sections. Required: QUERY (quote multiple words).')
    search.add_argument("query", metavar="QUERY", help='Search text, e.g. "project charter".')
    search.add_argument("--save", action="store_true", help="Save dated Markdown results in outputs/search/.")
    ask = commands.add_parser("ask", help='Answer from four retrieved sections and save evidence. Required: QUESTION in quotes.')
    ask.add_argument("question", metavar="QUESTION", help='Question, e.g. "What is a project?".')
    chat_parser = commands.add_parser("chat", help="Interactive local conversation. Use /help for session commands.")
    chat_parser.add_argument("--script", metavar="FILE", help="Read UTF-8 messages or commands, one per line.")
    commands.add_parser("help", help="Show this command overview. No inputs.")
    return parser


def main() -> int:
    """Dispatch a command and return its terminal exit code."""
    parser = build_parser()
    args = parser.parse_args()
    if args.command in (None, "help"):
        parser.print_help()
        return 0
    if args.command == "status":
        return status()
    if args.command == "ingest":
        from .ingest import ingest, rebuild_embeddings
        return rebuild_embeddings() if args.embeddings_only else ingest(force=args.force)
    if args.command == "search":
        from .search import search
        return search(args.query, save=args.save)
    if args.command == "ask":
        from .ask import ask
        return ask(args.question)
    if args.command == "chat":
        from .chat import chat
        return chat(args.script)
    return 0
