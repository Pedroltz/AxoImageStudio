"""Fast offline tests for backend primitives."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from comfy_backend.wildcards import expand
from comfy_backend.characters import CharacterStore
from comfy_backend.client import ComfyClient


class WildcardsTest(unittest.TestCase):
    def test_repeatable(self):
        with TemporaryDirectory() as d:
            Path(d, "clothes.txt").write_text("red\nblue\ngreen\n")
            self.assertEqual(expand("__clothes__", d, seed=42), expand("__clothes__", d, seed=42))

    def test_nested(self):
        with TemporaryDirectory() as d:
            Path(d, "outer.txt").write_text("__inner__\n")
            Path(d, "inner.txt").write_text("sunset\n")
            self.assertEqual(expand("__outer__", d), "sunset")

    def test_cycle(self):
        with TemporaryDirectory() as d:
            Path(d, "loop.txt").write_text("__loop__\n")
            self.assertEqual(expand("__loop__", d), "__loop__")

    def test_invalid_path(self):
        with TemporaryDirectory() as d:
            self.assertEqual(expand("__../secret__", d), "__../secret__")


class CharacterTest(unittest.TestCase):
    def test_store(self):
        with TemporaryDirectory() as d:
            store = CharacterStore(d)
            store.save("sidecut", "black hair")
            self.assertEqual(store.get("sidecut")["prompt"], "black hair")
            self.assertEqual(store.list(), ["sidecut"])

    def test_traversal(self):
        with TemporaryDirectory() as d:
            store = CharacterStore(d)
            with self.assertRaises(ValueError):
                store.save("../bad", "prompt")


class ClientTest(unittest.TestCase):
    def test_local_only(self):
        with self.assertRaises(ValueError):
            ComfyClient("http://example.org:8188")

    def test_workflow_validation(self):
        with self.assertRaises(ValueError):
            ComfyClient().submit({})


if __name__ == "__main__":
    unittest.main()
