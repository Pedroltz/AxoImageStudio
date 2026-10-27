"""Seeded, bounded wildcard expansion independent of any UI framework."""
from pathlib import Path
import random
import re

TOKEN = re.compile(r"__([a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_-]+)*)__")


def expand(prompt: str, directory: str | Path, seed: int = 0, maximum_depth: int = 8) -> str:
    root = Path(directory).resolve()
    rng = random.Random(seed)
    value = str(prompt)
    seen = {value}
    for _ in range(maximum_depth):
        def replace(match):
            filename = (root / (match.group(1) + ".txt")).resolve()
            if not filename.is_relative_to(root) or not filename.is_file():
                return match.group(0)
            choices = [
                line.strip() for line in filename.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.lstrip().startswith("#")
            ]
            return rng.choice(choices) if choices else match.group(0)

        updated = TOKEN.sub(replace, value)
        if updated == value:
            return updated
        if updated in seen:
            raise ValueError("Cyclic wildcard expansion detected")
        seen.add(updated)
        value = updated
    if TOKEN.search(value):
        raise ValueError("Maximum wildcard expansion depth exceeded")
    return value
