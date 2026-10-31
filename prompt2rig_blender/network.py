import json
import os
import urllib.request
import urllib.error
from urllib.parse import urljoin

def _url(base, path):
    return base.rstrip("/") + "/" + path.lstrip("/")

def request_json(base, path, payload=None, timeout=120):
    data = None
    headers = {"Accept": "application/json", "User-Agent": "Prompt2Rig-Blender/0.2"}
    method = "GET"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
        method = "POST"
    req = urllib.request.Request(_url(base, path), data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(detail)
            detail = parsed.get("error", detail)
        except Exception:
            pass
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except Exception as exc:
        raise RuntimeError(str(exc)) from exc

def check_server(base, timeout=5):
    return request_json(base, "/", timeout=timeout)

def upload_file(base, filepath, filename=None, timeout=120):
    """POST a file to /api/upload (multipart). Returns parsed JSON response."""
    import urllib.parse
    import mimetypes
    filepath = str(filepath)
    if not os.path.isfile(filepath):
        raise FileNotFoundError(filepath)
    filename = filename or os.path.basename(filepath)
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    boundary = "---- blender-p2r-boundary" + str(os.getpid()).replace("-", "")
    body = b""
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            body += b"--" + boundary.encode("utf-8") + b"\r\n"
            body += b'Content-Disposition: form-data; name="file"; filename="{}"\r\n'.format(filename.encode("utf-8")).encode("utf-8")
            body += b"Content-Type: " + content_type.encode("utf-8") + b"\r\n\r\n"
            body += chunk + b"\r\n"
    body += b"--" + boundary.encode("utf-8") + b"--\r\n"
    headers = {
        "Accept": "application/json",
        "Content-Type": "multipart/form-data; boundary=" + boundary,
        "User-Agent": "Prompt2Rig-Blender/0.2",
    }
    req = urllib.request.Request(_url(base, "/api/upload"), data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(detail)
            detail = parsed.get("error", detail)
        except Exception:
            pass
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except Exception as exc:
        raise RuntimeError(str(exc)) from exc

def fetch_bytes(base, url, timeout=120):
    """GET raw bytes (e.g. video_url, image_url) with Range support."""
    full = _url(base, url) if url.startswith("/") else url
    headers = {"User-Agent": "Prompt2Rig-Blender/0.2"}
    try:
        with urllib.request.urlopen(urllib.request.Request(full, headers=headers), timeout=timeout) as response:
            return response.read()
    except Exception as exc:
        raise RuntimeError(str(exc)) from exc
