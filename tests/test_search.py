"""Fast offline tests for retrieval math and the no-generation boundary."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from wiki_cli import config
from wiki_cli.search import tokenize, normalize, combine_scores, retrieve
from wiki_cli.ingest import rebuild_embeddings


class SearchTests(unittest.TestCase):
    def test_tokenization(self):
        self.assertEqual(tokenize("Scope, COST/time! (2026) — café_name"),
                         ["scope", "cost", "time", "2026", "café", "name"])
        self.assertEqual(tokenize(" -- ... "), [])

    def test_normalization(self):
        np.testing.assert_allclose(normalize([-2, 0, 6]), [0, 0.25, 1])
        np.testing.assert_array_equal(normalize([3, 3, 3]), [0, 0, 0])
        np.testing.assert_array_equal(normalize([0]), [0])
        self.assertEqual(normalize([]).size, 0)
        with self.assertRaises(ValueError):
            normalize([float("nan")])

    def test_combination(self):
        with patch.object(config, "KEYWORD_WEIGHT", 0.5), patch.object(config, "SEMANTIC_WEIGHT", 0.5):
            final, keyword, semantic = combine_scores([0, 20, 40], [-1, 1, 0])
        np.testing.assert_allclose(keyword, [0, 0.5, 1])
        np.testing.assert_allclose(semantic, [0, 1, 0.5])
        np.testing.assert_allclose(final, [0, 0.75, 0.75])
        with self.assertRaises(ValueError):
            combine_scores([1], [1, 2])

    def test_search_uses_query_prompt_and_only_embed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            chunks = [{"source_file": "source.md", "section_number": i,
                       "section_heading": f"{i}. Heading", "text": text}
                      for i, text in enumerate(["charter objectives", "cost budget"], 1)]
            (root / "chunks.json").write_text(json.dumps({"chunks": chunks,
                "embedding_model": config.EMBEDDING_MODEL,
                "document_format": config.EMBEDDING_DOCUMENT_FORMAT}), encoding="utf-8")
            np.save(root / "embeddings.npy", [[1., 0.], [0., 1.]])
            with patch.object(config, "DATA_DIR", root), patch("wiki_cli.search.ollama.Client") as factory:
                client = factory.return_value
                client.embed.return_value.embeddings = [[1., 0.]]
                result = retrieve("charter")
                self.assertEqual(len(result["results"]), 2)
                self.assertEqual(client.embed.call_args.kwargs["input"], "task: search result | query: charter")
                self.assertEqual(client.embed.call_args.kwargs["model"], config.EMBEDDING_MODEL)
                client.generate.assert_not_called()
                client.chat.assert_not_called()
                np.testing.assert_allclose(sorted(r["semantic_raw"] for r in result["results"]), [0, 1])
                # Legacy embeddings must be rejected before making an Ollama call.
                (root / "chunks.json").write_text(json.dumps({"chunks": chunks}))
                client.embed.reset_mock()
                with self.assertRaisesRegex(ValueError, "outdated"):
                    retrieve("charter")
                client.embed.assert_not_called()

    def test_embeddings_only_does_not_write_vault_or_call_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root / "vault/raw"
            raw.mkdir(parents=True)
            source = raw / "source.md"
            source.write_text("## 1. Heading\nA project is temporary.\n")
            with patch.multiple(config, RAW_DIR=raw, DATA_DIR=root / "data"), patch("wiki_cli.ingest.ollama.Client") as factory, patch("wiki_cli.ingest.write_index") as index:
                client = factory.return_value
                client.embed.return_value.embeddings = [[0.5, 0.5]]
                original = source.read_bytes()
                self.assertEqual(rebuild_embeddings(), 0)
                self.assertEqual(source.read_bytes(), original)
                self.assertEqual(client.embed.call_args.kwargs["input"], "title: 1. Heading | text: A project is temporary.")
                client.generate.assert_not_called()
                index.assert_not_called()
                self.assertEqual(list((root / "vault").rglob("*.md")), [source])


if __name__ == "__main__":
    unittest.main()
