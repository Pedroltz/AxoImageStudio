"""Minimal ComfyUI REST client (localhost only by default)."""
import json
from urllib.parse import urlparse
import requests


class ComfyClient:
    def __init__(self, base_url="http://127.0.0.1:8188", timeout=45, allow_remote=False):
        parsed = urlparse(base_url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise ValueError("Invalid ComfyUI URL")
        if not allow_remote and parsed.hostname not in ("localhost", "127.0.0.1", "::1"):
            raise ValueError("Remote ComfyUI endpoints require explicit opt-in")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _request(self, method, route, **kwargs):
        response = self.session.request(method, self.base_url + route,
                                        timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response

    def submit(self, workflow, client_id=None):
        if not isinstance(workflow, dict) or not workflow:
            raise ValueError("Workflow must be a non-empty API-format dict")
        payload = {"prompt": workflow}
        if client_id:
            payload["client_id"] = str(client_id)
        result = self._request("POST", "/prompt", json=payload).json()
        if not result.get("prompt_id"):
            raise RuntimeError("ComfyUI returned no prompt_id")
        return result

    def history(self, prompt_id):
        return self._request("GET", "/history/" + str(prompt_id)).json()

    def queue(self):
        return self._request("GET", "/queue").json()

    def upload_image(self, filepath, subfolder="axo"):
        from pathlib import Path
        path = Path(filepath)
        with path.open("rb") as fp:
            return self._request("POST", "/upload/image",
                files={"image": (path.name, fp, "application/octet-stream")},
                data={"type": "input", "subfolder": subfolder, "overwrite": "false"}).json()

    def image(self, filename, subfolder="", kind="output"):
        return self._request("GET", "/view", params={
            "filename": filename, "subfolder": subfolder, "type": kind
        }).content
