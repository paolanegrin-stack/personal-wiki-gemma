"""Routing, memory, and chat control tests; Ollama is mocked."""

import contextlib
import io
import json
import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from wiki_cli import config
from wiki_cli.chat import parse_route, recent_history, history_messages, ChatSession, chat


def response(text):
    return SimpleNamespace(message=SimpleNamespace(content=text), done_reason="stop")


class ChatTests(unittest.TestCase):
    def test_route_parser(self):
        self.assertEqual(parse_route("SEARCH"), "SEARCH")
        self.assertEqual(parse_route(" NO_SEARCH\n"), "NO_SEARCH")
        for invalid in ("", "no_search", "search", "NO_SEARCH.", "SEARCH because...",
                        '"NO_SEARCH"', "```NO_SEARCH```", "SEARCH NO_SEARCH", "Maybe"):
            self.assertEqual(parse_route(invalid), "SEARCH")

    def test_history_limit_keeps_pairs(self):
        history = [{"message": str(i), "answer": f"answer {i}"} for i in range(9)]
        kept = recent_history(history, 6)
        self.assertEqual([t["message"] for t in kept], ["3", "4", "5", "6", "7", "8"])
        self.assertEqual(len(history_messages(kept)), 12)
        self.assertEqual(recent_history(history, 0), [])
        self.assertEqual(recent_history(history, 12), history)
        self.assertEqual(len(history), 9)
        with self.assertRaises(ValueError):
            recent_history(history, -1)

    def test_routes_enforce_retrieval_and_pass_history(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            with patch.object(config, "OUTPUTS_DIR", Path(directory)), patch("wiki_cli.chat.ollama.Client") as factory, patch("wiki_cli.chat.retrieve") as retrieve:
                client = factory.return_value
                client.chat.side_effect = [response("NO_SEARCH"), response("Hello!"),
                                           response("invalid route"), response("How can scope creep be prevented?"),
                                           response("Define scope [1].")]
                session = ChatSession()
                first = session.answer("Hi")
                retrieve.assert_not_called()
                self.assertEqual(first["route"], "NO_SEARCH")
                passage = {"rank": 1, "source_file": "source.md", "section_number": 3,
                           "section_heading": "3. Scope", "text": "Define scope.", "final": 1.0}
                retrieve.return_value = {"results": [passage]}
                second = session.answer("How can a team prevent it?")
                retrieve.assert_called_once_with("How can scope creep be prevented?")
                self.assertEqual(second["route"], "SEARCH")
                self.assertIn("fell back", second["warnings"][0])
                self.assertEqual(second["check"]["used"], [1])
                routing_messages = client.chat.call_args_list[2].kwargs["messages"]
                self.assertEqual([m["role"] for m in routing_messages], ["system", "user"])
                self.assertEqual(json.loads(routing_messages[1]["content"]),
                                 {"previous_user_message": "Hi", "new_user_message": "How can a team prevent it?"})
                self.assertNotIn("Hello!", routing_messages[1]["content"])
                for call in client.chat.call_args_list[3:]:
                    self.assertEqual(call.kwargs["messages"][1:3],
                                     [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello!"}])
                    self.assertIs(call.kwargs["think"], False)
                self.assertIn("Read all passages before answering", client.chat.call_args.kwargs["messages"][0]["content"])
                self.assertIn("Define scope.", session.path.read_text(encoding="utf-8"))
                session.reset()
                self.assertEqual(session.history, [])
                self.assertIsNone(session.previous_user)
                self.assertEqual(session.last_sources, [])
                self.assertEqual(len(session.turns), 2)

    def test_session_enforces_history_limit(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            with patch.object(config, "OUTPUTS_DIR", Path(directory)), patch.object(config, "CHAT_HISTORY_TURNS", 2), patch("wiki_cli.chat.ollama.Client") as factory:
                factory.return_value.chat.side_effect = [response("NO_SEARCH"), response("Hi")] * 4
                session = ChatSession()
                for message in ("one", "two", "three", "four"):
                    session.answer(message)
                self.assertEqual([t["message"] for t in session.history], ["three", "four"])
                self.assertEqual([t["history_turns"] for t in session.turns], [0, 1, 2, 2])
                self.assertEqual(len(factory.return_value.chat.call_args.kwargs["messages"]), 6)

    def test_router_versions_and_user_only_input(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            with patch.object(config, "OUTPUTS_DIR", Path(directory)), patch("wiki_cli.chat.ollama.Client") as factory:
                session = ChatSession()
                history = [{"message": "Older user", "answer": "Secret assistant answer"},
                           {"message": "Latest user", "answer": "Another assistant answer"}]
                session.previous_user = "Latest user"
                session.route("Follow-up?", history)
                messages = factory.return_value.chat.call_args.kwargs["messages"]
                self.assertEqual(len(messages), 2)
                self.assertEqual(json.loads(messages[-1]["content"]),
                                 {"previous_user_message": "Latest user", "new_user_message": "Follow-up?"})
                self.assertNotIn("assistant", [m["role"] for m in messages])
                self.assertNotIn("Older user", messages[-1]["content"])
                self.assertIn("Router prompt version: v2", session.path.read_text())
                session.reset()
                session.route("New start", [])
                self.assertIsNone(json.loads(factory.return_value.chat.call_args.kwargs["messages"][-1]["content"])["previous_user_message"])
                session.router_version = "v1"
                session.route("Follow-up?", history)
                messages = factory.return_value.chat.call_args.kwargs["messages"]
                self.assertEqual(messages[1:-1], history_messages(history))
                prompt = (config.PROMPTS_DIR / "router-v1.md").read_bytes()
                self.assertEqual(hashlib.sha256(prompt).hexdigest(), "1323e0e6c3a63eca5513f3224955d7397edae4c572b63b018a6e2009815ae8a3")

    def test_commands_do_not_call_answer(self):
        with patch("wiki_cli.chat.ChatSession") as factory, patch("builtins.input", side_effect=["/help", "/sources", "/reset", "/quit"]), contextlib.redirect_stdout(io.StringIO()):
            session = factory.return_value
            session.turns = []
            session.events = []
            session.last_sources = ["[1] -> source.md"]
            self.assertEqual(chat(), 0)
            session.answer.assert_not_called()
            session.reset.assert_called_once()
            session.save.assert_called()


if __name__ == "__main__":
    unittest.main()
