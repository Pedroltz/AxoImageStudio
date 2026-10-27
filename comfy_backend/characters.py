"""Small JSON character library. Images are copied to a controlled location."""
from pathlib import Path
import json
import re
import shutil

VALID_NAME = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


class CharacterStore:
    def __init__(self, directory):
        self.root = Path(directory).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _folder(self, name):
        if not VALID_NAME.fullmatch(name):
            raise ValueError("Invalid character name")
        return self.root / name

    def save(self, name, prompt, images=()):
        folder = self._folder(name)
        folder.mkdir(parents=True, exist_ok=True)
        existing = self.get(name) if (folder / "character.json").exists() else {}
        references = list(existing.get("references", []))
        for source in images:
            source = Path(source)
            if source.suffix.lower() not in IMAGE_EXTENSIONS or not source.is_file():
                raise ValueError("Unsupported reference image")
            if source.stat().st_size > 25 * 1024 * 1024:
                raise ValueError("Image is too large")
            target = folder / f"reference_{len(references) + 1}{source.suffix.lower()}"
            shutil.copyfile(source, target)
            references.append(target.name)
        data = {"name": name, "prompt": str(prompt), "references": references}
        (folder / "character.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data

    def get(self, name):
        folder = self._folder(name)
        data = json.loads((folder / "character.json").read_text(encoding="utf-8"))
        if data.get("name") != name:
            raise ValueError("Character record mismatch")
        data["references"] = [
            value for value in data.get("references", [])
            if isinstance(value, str) and Path(value).name == value
            and (folder / value).is_file()
        ]
        return data

    def list(self):
        return sorted(p.name for p in self.root.iterdir()
                      if p.is_dir() and VALID_NAME.fullmatch(p.name)
                      and (p / "character.json").is_file())
