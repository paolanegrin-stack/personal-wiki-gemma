"""Central settings. All machine-generated retrieval files stay outside the vault."""

from pathlib import Path

# Resolve paths from this file, so the CLI also works from another directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
VAULT_DIR = PROJECT_ROOT / "vault"
RAW_DIR = VAULT_DIR / "raw"
WIKI_DIR = VAULT_DIR / "wiki"
INDEX_PATH = VAULT_DIR / "index.md"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
TESTS_DIR = PROJECT_ROOT / "tests"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Only the local Ollama server is used. No cloud service or API key is needed.
OLLAMA_HOST = "http://localhost:11434"
GENERATION_MODEL = "gemma4:e2b-it-qat"
EMBEDDING_MODEL = "embeddinggemma"
TOP_K = 4  # Return the top four raw-source sections.
STATUS_TIMEOUT_SECONDS = 300  # A cold model load can take time on a CPU.

INGEST_TIMEOUT_SECONDS = 900  # Per local request; allow slow CPU generation.

# Fixed hybrid weights; normalize each score list over the entire corpus first.
KEYWORD_WEIGHT = 0.5
SEMANTIC_WEIGHT = 0.5
EMBEDDING_DOCUMENT_FORMAT = "title: {title} | text: {content}"
EMBEDDING_QUERY_FORMAT = "task: search result | query: {content}"
SEARCH_TIMEOUT_SECONDS = 300

# Ask-mode generation settings; retrieval weights and TOP_K above are unchanged.
ASK_TEMPERATURE = 0.2
ASK_SEED = 42
ASK_NUM_CTX = 8192
ASK_NUM_PREDICT = 1024
ASK_TIMEOUT_SECONDS = 900
INSUFFICIENT_EVIDENCE = "I don't have enough evidence in my notes to answer this."

ASK_PROMPT_VERSION = "v2"  # Select prompts/ask-v1.md or prompts/ask-v2.md.

# One chat turn is a user message and its assistant answer.
CHAT_HISTORY_TURNS = 6
CHAT_ROUTE_TOKENS = 8
CHAT_QUERY_TOKENS = 96

ROUTER_PROMPT_VERSION = "v2"  # Routing prompt and input policy only.
