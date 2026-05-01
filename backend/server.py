#!/usr/bin/env python3
"""Lightweight backend for the NovaTech AI Solutions demo site."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
LEADS_FILE = ROOT / "backend" / "data" / "leads.json"
MESSAGES_FILE = ROOT / "backend" / "data" / "messages.json"


def _append_record(path: Path, record: dict[str, Any]) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)

  if path.exists():
    with path.open("r", encoding="utf-8") as stream:
      payload = json.load(stream)
      records = payload if isinstance(payload, list) else []
  else:
    records = []

  records.append(record)
  with path.open("w", encoding="utf-8") as stream:
    json.dump(records, stream, indent=2)


def _bot_reply(message: str) -> str:
  prompt = message.strip().lower()

  if any(keyword in prompt for keyword in ("price", "cost", "pricing")):
    return "Our plans start from $299/month. We can create a custom plan after a short discovery call."

  if any(keyword in prompt for keyword in ("demo", "meeting", "call")):
    return "Absolutely. Share your name and email in the contact form and we can schedule a demo this week."

  if any(keyword in prompt for keyword in ("integration", "api", "crm", "whatsapp")):
    return "Yes, we support API-based integrations and can connect with CRM, website chat, and messaging channels."

  if any(keyword in prompt for keyword in ("support", "hours", "24/7")):
    return "The bot can run 24/7 for first-level support and escalate complex issues to your team."

  return "Thanks for your message. I can help with pricing, demos, integrations, and support setup."


class Handler(SimpleHTTPRequestHandler):
  def __init__(self, *args: Any, **kwargs: Any):
    super().__init__(*args, directory=str(ROOT), **kwargs)

  def do_GET(self) -> None:
    if self.path == "/api/health":
      self._send_json(HTTPStatus.OK, {"status": "ok", "time": datetime.now(timezone.utc).isoformat()})
      return

    super().do_GET()

  def do_POST(self) -> None:
    if self.path == "/api/contact":
      self._handle_contact()
      return

    if self.path == "/api/support-bot":
      self._handle_support_bot()
      return

    self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})

  def _read_json(self) -> dict[str, Any]:
    length = int(self.headers.get("Content-Length", "0"))
    raw = self.rfile.read(length) if length > 0 else b"{}"

    try:
      payload = json.loads(raw.decode("utf-8"))
      if not isinstance(payload, dict):
        raise ValueError("JSON object required")
      return payload
    except Exception:
      raise ValueError("Invalid JSON payload")

  def _handle_contact(self) -> None:
    try:
      payload = self._read_json()
    except ValueError as error:
      self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
      return

    required = ["name", "email", "company", "message"]
    missing = [field for field in required if not str(payload.get(field, "")).strip()]
    if missing:
      self._send_json(HTTPStatus.BAD_REQUEST, {"error": f"Missing required fields: {', '.join(missing)}"})
      return

    record = {
      "name": payload["name"].strip(),
      "email": payload["email"].strip(),
      "company": payload["company"].strip(),
      "message": payload["message"].strip(),
      "created_at": datetime.now(timezone.utc).isoformat(),
    }

    _append_record(LEADS_FILE, record)
    self._send_json(HTTPStatus.CREATED, {"message": "Lead captured"})

  def _handle_support_bot(self) -> None:
    try:
      payload = self._read_json()
    except ValueError as error:
      self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
      return

    message = str(payload.get("message", "")).strip()
    if not message:
      self._send_json(HTTPStatus.BAD_REQUEST, {"error": "message is required"})
      return

    record = {
      "message": message,
      "reply": _bot_reply(message),
      "created_at": datetime.now(timezone.utc).isoformat(),
    }

    _append_record(MESSAGES_FILE, record)
    self._send_json(HTTPStatus.OK, {"reply": record["reply"]})

  def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
    encoded = json.dumps(payload).encode("utf-8")
    self.send_response(status)
    self.send_header("Content-Type", "application/json; charset=utf-8")
    self.send_header("Content-Length", str(len(encoded)))
    self.end_headers()
    self.wfile.write(encoded)


if __name__ == "__main__":
  server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
  print("Serving website + API at http://127.0.0.1:8000")
  try:
    server.serve_forever()
  except KeyboardInterrupt:
    print("\nShutting down server")
    server.server_close()
