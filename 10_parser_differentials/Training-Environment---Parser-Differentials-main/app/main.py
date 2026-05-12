#!/usr/bin/env python3
import json
import os
import posixpath
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

FLAG = os.getenv("FLAG", "WSL{mind_the_interpretation_gap}")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))


def parse_json_first_key(raw: bytes):
    """Gateway-style JSON parser: preserve the first value for duplicate keys."""
    def first_key_object(pairs):
        obj = {}
        for key, value in pairs:
            if key not in obj:
                obj[key] = value
        return obj

    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"), object_pairs_hook=first_key_object)


def parse_json_last_key(raw: bytes):
    """Backend-style JSON parser: Python's default behavior keeps the last duplicate key."""
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def legacy_backend_normalize(raw_path: str) -> str:
    """
    Legacy backend route normalizer.

    Bug: it performs repeated URL decoding before path normalization, while the gateway
    made its allow/deny decision on the raw path.
    """
    decoded = raw_path
    for _ in range(2):
        decoded = unquote(decoded)
    normalized = posixpath.normpath(decoded)
    if not normalized.startswith("/"):
        normalized = "/" + normalized
    return normalized


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict):
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def gateway_check(method: str, raw_path: str, headers, body: bytes):
    """
    Front gateway policy.

    It only allows public API routes and public report scope. The weakness is not the
    policy itself, but that it interprets the request differently from the backend.
    """
    if not raw_path.startswith("/api/public/"):
        return False, "gateway: only /api/public/** is reachable from outside"

    content_type = headers.get("Content-Type", "")
    if method == "POST" and "application/json" in content_type:
        try:
            data = parse_json_first_key(body)
        except Exception:
            return False, "gateway: invalid json"

        scope = data.get("scope", "public")
        if scope != "public":
            return False, "gateway: report scope must be public"

    return True, "ok"


def backend_dispatch(handler: BaseHTTPRequestHandler, normalized_path: str, body: bytes):
    """Backend application routes after legacy decoding and normalization."""
    if normalized_path == "/api/public/status":
        return json_response(handler, 200, {
            "ok": True,
            "service": "report-gateway",
            "message": "public status endpoint is healthy",
        })

    if normalized_path == "/api/public/report":
        return json_response(handler, 200, {
            "title": "Public Report",
            "scope": "public",
            "data": ["training", "parser", "differential"],
        })

    if normalized_path == "/api/internal/report":
        try:
            data = parse_json_last_key(body)
        except Exception:
            return json_response(handler, 400, {"error": "backend: invalid json"})

        if data.get("scope") != "internal":
            return json_response(handler, 403, {
                "error": "backend: internal scope required",
                "backend_path": normalized_path,
                "hint": "The gateway and backend do not agree on everything.",
            })

        return json_response(handler, 200, {
            "title": "Internal Security Report",
            "scope": "internal",
            "flag": FLAG,
        })

    return json_response(handler, 404, {
        "error": "backend: route not found",
        "backend_path": normalized_path,
    })


class ChallengeHandler(BaseHTTPRequestHandler):
    server_version = "ParserDifferentialLab/1.0"

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def handle_request(self):
        raw_path = self.path.split("?", 1)[0]
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(content_length) if content_length else b""

        allowed, reason = gateway_check(self.command, raw_path, self.headers, body)
        if not allowed:
            return json_response(self, 403, {
                "error": reason,
                "gateway_path": raw_path,
            })

        backend_path = legacy_backend_normalize(raw_path)
        return backend_dispatch(self, backend_path, body)

    def log_message(self, fmt, *args):
        print("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), fmt % args))


if __name__ == "__main__":
    print(f"[+] Parser Differential Lab listening on http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), ChallengeHandler).serve_forever()
