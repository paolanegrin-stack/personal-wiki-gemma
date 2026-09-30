"""Simple hybrid search: BM25 keywords plus local EmbeddingGemma cosine similarity."""

from datetime import datetime
import json
import re
import sys
from time import perf_counter

import numpy as np
import ollama
from rank_bm25 import BM25Okapi

from . import config


def tokenize(text):
    """Lowercase and split at punctuation/whitespace; retain letters and numbers."""
    return re.findall(r"[^\W_]+", text.lower(), flags=re.UNICODE)


def normalize(scores):
    """Min-max scale across all chunks. Equal scores carry no ranking signal."""
    values = np.asarray(scores, dtype=float)
    if values.ndim != 1 or not np.isfinite(values).all():
        raise ValueError("Scores must be a finite one-dimensional array")
    if values.size == 0:
        return values.copy()
    low, high = values.min(), values.max()
    if high == low:
        return np.zeros_like(values)
    return (values - low) / (high - low)


def combine_scores(keyword, semantic):
    """Normalize independently, then apply the fixed weights from config.py."""
    keyword = normalize(keyword)
    semantic = normalize(semantic)
    if keyword.shape != semantic.shape:
        raise ValueError("Keyword and semantic scores must have the same length")
    final = config.KEYWORD_WEIGHT * keyword + config.SEMANTIC_WEIGHT * semantic
    return final, keyword, semantic


def retrieve(query):
    """Return top results and timing. This uses embed(), never generate() or chat()."""
    started = perf_counter()
    tokens = tokenize(query)
    if not tokens:
        raise ValueError("Enter a query containing at least one letter or number")
    metadata = json.loads((config.DATA_DIR / "chunks.json").read_text(encoding="utf-8"))
    if (metadata.get("embedding_model") != config.EMBEDDING_MODEL
            or metadata.get("document_format") != config.EMBEDDING_DOCUMENT_FORMAT):
        raise ValueError("Embedding model or document format is outdated; run wiki ingest --embeddings-only")
    chunks = metadata["chunks"]
    vectors = np.load(config.DATA_DIR / "embeddings.npy", allow_pickle=False)
    if (not chunks or vectors.ndim != 2 or vectors.shape[0] != len(chunks)
            or not np.isfinite(vectors).all()):
        raise ValueError("Invalid or mismatched retrieval data; run wiki ingest --embeddings-only")
    norms = np.linalg.norm(vectors, axis=1)
    if np.any(norms == 0):
        raise ValueError("Stored embeddings contain zero vectors; rebuild embeddings")
    documents = [tokenize(c["section_heading"] + "\n" + c["text"]) for c in chunks]
    if not any(documents):
        raise ValueError("The stored chunks contain no searchable words")
    keyword_raw = BM25Okapi(documents).get_scores(tokens)
    client = ollama.Client(host=config.OLLAMA_HOST, timeout=config.SEARCH_TIMEOUT_SECONDS, trust_env=False)
    response = client.embed(model=config.EMBEDDING_MODEL,
                            input=config.EMBEDDING_QUERY_FORMAT.format(content=query.strip()),
                            truncate=False)
    query_vector = np.asarray(response.embeddings[0], dtype=float)
    if (query_vector.shape != (vectors.shape[1],) or not np.isfinite(query_vector).all()
            or np.linalg.norm(query_vector) == 0):
        raise ValueError("Invalid query embedding or dimension mismatch; rebuild embeddings")
    semantic_raw = vectors @ query_vector / (norms * np.linalg.norm(query_vector))
    semantic_raw = np.clip(semantic_raw, -1, 1)
    final, keyword, semantic = combine_scores(keyword_raw, semantic_raw)
    # Stable sorting uses stored chunk order as the tie-breaker.
    order = np.argsort(-final, kind="stable")[:config.TOP_K]
    results = []
    for rank, index in enumerate(order, 1):
        chunk = chunks[index]
        preview = " ".join(chunk["text"].split())
        results.append({"rank": rank, "final": float(final[index]),
                        "keyword": float(keyword[index]), "semantic": float(semantic[index]),
                        "keyword_raw": float(keyword_raw[index]), "semantic_raw": float(semantic_raw[index]),
                        "source_file": chunk["source_file"], "section_number": chunk["section_number"],
                        "section_heading": chunk["section_heading"], "text": chunk["text"],
                        "preview": preview[:200] + ("..." if len(preview) > 200 else "")})
    return {"query": query, "date": datetime.now().astimezone().isoformat(timespec="seconds"),
            "seconds": perf_counter() - started, "results": results}


def format_results(report):
    """Use the same readable Markdown for terminal output and saved evidence."""
    lines = ["# Search results", "", f"Date: {report['date']}", f"Query: {report['query']}",
             f"Search time: {report['seconds']:.3f} seconds", "",
             f"Final = {config.KEYWORD_WEIGHT} × keyword + {config.SEMANTIC_WEIGHT} × semantic.",
             "Keyword and semantic scores are independently min-max normalized over all chunks.",
             "Scores rank these chunks; they are not confidence or evidence-sufficiency probabilities.", ""]
    for result in report["results"]:
        lines.extend([f"## {result['rank']}. {result['section_heading']}", "",
                      f"Final: {result['final']:.4f} | Keyword: {result['keyword']:.4f} | Semantic: {result['semantic']:.4f}",
                      f"Raw BM25: {result['keyword_raw']:.4f} | Raw cosine: {result['semantic_raw']:.4f}",
                      f"Source: vault/raw/{result['source_file']}",
                      f"Section: {result['section_number']} — {result['section_heading']}", "",
                      result["preview"], ""])
    return "\n".join(lines)


def search(query, save=False):
    """CLI boundary: report useful errors without a stack trace."""
    try:
        report = retrieve(query)
        text = format_results(report)
        print(text)
        if save:
            directory = config.OUTPUTS_DIR / "search"
            directory.mkdir(parents=True, exist_ok=True)
            # A timestamp plus an ASCII slug is safe on Windows and avoids overwrites.
            slug = re.sub(r"[^a-z0-9]+", "-", query.lower()).strip("-")[:70] or "query"
            filename = datetime.now().strftime("%Y%m%d-%H%M%S-%f") + "-" + slug + ".md"
            path = directory / filename
            with path.open("x", encoding="utf-8") as handle:
                handle.write(text)
            print(f"Saved: {path}")
        return 0
    except Exception as error:
        print(f"Error: {error}\nCheck local Ollama and embeddinggemma. "
              "If data is missing or outdated, run 'wiki ingest --embeddings-only'.", file=sys.stderr)
        return 1
