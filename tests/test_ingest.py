"""Offline ingestion checks using temporary files and a fake Ollama client."""

import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from wiki_cli import config
from wiki_cli.ingest import ingest, read_chunks, clean_links, render_note, clean_related_notes


class IngestTests(unittest.TestCase):
    def test_sections_and_fenced_headings(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.md"
            text = "# Title\nPreamble\n## 1. First\nFact\n```md\n## 99. Not a heading\n```\n### Subheading\nMore\n## 2. Second\nOther fact\n"
            path.write_text(text, encoding="utf-8")
            chunks = read_chunks(Path(directory))
            self.assertEqual([c["section_number"] for c in chunks], [1, 2])
            self.assertIn("### Subheading", chunks[0]["text"])
            self.assertNotIn("Preamble", chunks[0]["text"])
            self.assertEqual(path.read_text(encoding="utf-8"), text)

    def test_links(self):
        text, removed = clean_links("[[Good]] [[Bad]] [[Bad|label]]", {"Good"})
        self.assertEqual(text, "[[Good]] Bad label")
        self.assertEqual(removed, ["[[Bad]]", "[[Bad|label]]"])

    def test_related_self_links_and_duplicates(self):
        names = ["Example", "Other", "Other", " Example ", "Third", " Other "]
        kept, removed = clean_related_notes(names, "Example")
        self.assertEqual(kept, ["Other", "Third"])
        self.assertEqual(removed, [
            "[[Example]] (self-link)", "[[Other]] (duplicate)",
            "[[Example]] (self-link)", "[[Other]] (duplicate)",
        ])
        self.assertEqual(names[0], "Example")  # The input list is not mutated.
        self.assertEqual(clean_related_notes(kept, "Example"), (kept, []))
        self.assertEqual(clean_related_notes([], "Example"), ([], []))

    def test_skip_force_and_embedding_alignment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = {"RAW_DIR": root / "raw", "WIKI_DIR": root / "wiki",
                     "DATA_DIR": root / "data", "OUTPUTS_DIR": root / "outputs",
                     "PROMPTS_DIR": root / "prompts", "INDEX_PATH": root / "index.md"}
            for name in ("RAW_DIR", "PROMPTS_DIR"):
                paths[name].mkdir()
            raw = paths["RAW_DIR"] / "source.md"
            raw.write_text("## 1. First\nA project is temporary.\n", encoding="utf-8")
            original = raw.read_bytes()
            (paths["PROMPTS_DIR"] / "wiki-instructions.md").write_text("Use only sources.")
            note = {"summary": ["A project is temporary.", "It ends."],
                    "summary_sources": ["source.md::1"],
                    "key_points": [{"text": "A project is temporary.", "sources": ["source.md::1"]}],
                    "related_notes": ["Example", "Invented", "Invented"]}
            plan = [("Concepts", "Example", "An example.", [("source.md", [1])])]
            with patch.multiple(config, **paths), patch("wiki_cli.ingest.NOTE_PLAN", plan), patch("wiki_cli.ingest.ollama.Client") as factory:
                client = factory.return_value
                client.list.return_value.models = [SimpleNamespace(model=config.GENERATION_MODEL), SimpleNamespace(model=config.EMBEDDING_MODEL + ":latest")]
                client.embed.return_value.embeddings = [[0.25, 0.75]]
                client.generate.return_value = SimpleNamespace(response=json.dumps(note), done_reason="stop")
                self.assertEqual(ingest(), 0)
                self.assertEqual(client.generate.call_count, 1)
                self.assertIs(client.generate.call_args.kwargs["think"], False)
                target = paths["WIKI_DIR"] / "Concepts/Example.md"
                self.assertNotIn("[[Invented]]", target.read_text())
                self.assertNotIn("[[Example]]", target.read_text())
                log = (paths["OUTPUTS_DIR"] / "ingest-log.md").read_text()
                self.assertIn("[[Example]] (self-link)", log)
                self.assertIn("[[Invented]] (duplicate)", log)
                self.assertIn("[[Invented]]", (paths["OUTPUTS_DIR"] / "ingest-log.md").read_text())
                saved = json.loads((paths["DATA_DIR"] / "chunks.json").read_text())
                self.assertEqual(saved["chunks"][0]["source_file"], "source.md")
                self.assertEqual(np.load(paths["DATA_DIR"] / "embeddings.npy").shape, (1, 2))
                target.write_text("Manual edits", encoding="utf-8")
                self.assertEqual(ingest(), 0)
                self.assertEqual(target.read_text(), "Manual edits")
                self.assertEqual(client.generate.call_count, 1)
                self.assertEqual(ingest(force=True), 0)
                self.assertEqual(client.generate.call_count, 2)
                self.assertNotEqual(target.read_text(), "Manual edits")
                self.assertEqual(raw.read_bytes(), original)
                note["summary_sources"] = ["unapproved"]
                with self.assertRaises(ValueError):
                    render_note(note, "Concepts", "Example", saved["chunks"], "2026-09-29")


if __name__ == "__main__":
    unittest.main()
