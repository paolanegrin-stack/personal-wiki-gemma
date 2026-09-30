"""Citation checks are deterministic and never call Ollama."""

import hashlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from wiki_cli import config
from wiki_cli.ask import check_citations, run_ask, build_prompt


class CitationTests(unittest.TestCase):
    def setUp(self):
        self.passages = [{"rank": 1, "source_file": "first.md", "section_number": 3,
                          "section_heading": "3. First", "text": "Full first passage.", "final": 0.9},
                         {"rank": 2, "source_file": "second.md", "section_number": 5,
                          "section_heading": "5. Second", "text": "Full second passage.", "final": 0.8}]

    def test_valid_repeated_citations_and_mapping(self):
        check = check_citations("Claim [2]. Another [1]. Again [2].", self.passages)
        self.assertEqual(check["occurrences"], [2, 1, 2])
        self.assertEqual(check["used"], [2, 1])
        self.assertEqual(check["warnings"], [])
        self.assertIn("second.md, section 5", check["sources"][0])

    def test_invalid_citations(self):
        check = check_citations("Claim [0]. Another [9]. Valid [1].", self.passages)
        self.assertEqual(len(check["warnings"]), 2)
        self.assertIn("[0]", check["warnings"][0])
        self.assertIn("[9]", check["warnings"][1])
        self.assertEqual(len(check["sources"]), 1)

    def test_no_citations_and_exact_refusal(self):
        for answer in ("Uncited answer.", "", "I don't have enough evidence in my notes",
                       config.INSUFFICIENT_EVIDENCE + " Extra explanation."):
            self.assertEqual(len(check_citations(answer, self.passages)["warnings"]), 1)
        self.assertEqual(check_citations(config.INSUFFICIENT_EVIDENCE, self.passages)["warnings"], [])

    def test_references_must_exist_not_just_fit_list_length(self):
        check = check_citations("Claim [1].", [self.passages[1]])
        self.assertEqual(len(check["warnings"]), 1)

    def test_prompt_versions_preserve_v1_and_only_change_system_instructions(self):
        v1 = (config.PROMPTS_DIR / "ask-v1.md").read_bytes()
        self.assertEqual(hashlib.sha256(v1).hexdigest(), "d1880e3d7b4a4f9ecf11b8e5244773ac07e11503d6ff32e3ecc38f2e457404ff")
        v2 = (config.PROMPTS_DIR / "ask-v2.md").read_text(encoding="utf-8")
        self.assertTrue(v2.startswith(v1.decode("utf-8") + "\n\n"))
        self.assertEqual(len(v2[len(v1.decode("utf-8")) + 2:].split("\n\n")), 3)
        with patch.object(config, "ASK_PROMPT_VERSION", "v1"):
            system1, prompt1 = build_prompt("Question?", self.passages)
        with patch.object(config, "ASK_PROMPT_VERSION", "v2"):
            system2, prompt2 = build_prompt("Question?", self.passages)
        persona = (config.PROMPTS_DIR / "persona.md").read_text(encoding="utf-8")
        self.assertEqual(system1, persona + "\n\n" + v1.decode("utf-8"))
        self.assertEqual(system2, persona + "\n\n" + v2)
        self.assertEqual(prompt1, prompt2)

    def test_ask_prompt_settings_and_saved_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(config, "OUTPUTS_DIR", root), patch("wiki_cli.ask.retrieve") as retrieve, patch("wiki_cli.ask.ollama.Client") as factory:
                retrieve.return_value = {"results": self.passages, "seconds": 0.1}
                client = factory.return_value
                client.generate.return_value = SimpleNamespace(response="A claim [1].", done_reason="stop")
                report = run_ask("A question?")
                retrieve.assert_called_once_with("A question?")
                args = client.generate.call_args.kwargs
                self.assertIs(args["think"], False)
                self.assertEqual(args["options"]["temperature"], 0.2)
                self.assertEqual(args["options"]["seed"], config.ASK_SEED)
                self.assertIn(config.INSUFFICIENT_EVIDENCE, args["system"])
                self.assertIn("Full first passage.", args["prompt"])
                self.assertIn("[2] Source: vault/raw/second.md", args["prompt"])
                text = Path(report["saved_path"]).read_text(encoding="utf-8")
                self.assertIn("Full second passage.", text)
                self.assertIn("A claim [1].", text)
                self.assertIn(f"Prompt version: {config.ASK_PROMPT_VERSION}", text)
                self.assertIsNone(report["error"])
                retrieve.side_effect = ValueError("Test retrieval failure")
                failed = run_ask("Fail?")
                self.assertIn("Test retrieval failure", Path(failed["saved_path"]).read_text(encoding="utf-8"))
                self.assertEqual(client.generate.call_count, 1)


if __name__ == "__main__":
    unittest.main()
