"""
server.py  MoMo SMS REST API

Authentication: 
  Username: admin
  Password: momo2024

"""

import base64
import json
import re
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from parser import parse_xml
from dsa import build_index, linear_search, dict_lookup, benchmark

# loads transactions into memory. index is a hash map for O(1) lookups by ID

XML_FILE = "modified_sms_v2.xml"  
_transactions: list[dict] = parse_xml(XML_FILE)
_index: dict[int, dict] = build_index(_transactions)
_next_id: int = max((t["id"] for t in _transactions), default=0) + 1


def _refresh_index():
    global _index
    _index = build_index(_transactions)

# endpoint is protected by HTTP basic authentication.
VALID_CREDENTIALS = {
    "admin": "momo2024",
}

# checks the Authorization header for valid credentials.
def _check_auth(handler) -> bool:
    """Return True if the request carries valid Basic Auth credentials."""
    auth_header = handler.headers.get("Authorization", "")
    if not auth_header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
        username, password = decoded.split(":", 1)
        return VALID_CREDENTIALS.get(username) == password
    except Exception:
        return False

# helper to send JSON responses

def _send_json(handler, status: int, payload):
    body = json.dumps(payload, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _send_401(handler):
    handler.send_response(401)
    handler.send_header("WWW-Authenticate", 'Basic realm="MoMo API"')
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(json.dumps({"error": "Unauthorized. Provide valid Basic Auth credentials."}).encode())


def _parse_id(segment: str) -> int | None:
    try:
        return int(segment)
    except (ValueError, TypeError):
        return None


class MoMoHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        """Override to add timestamp to logs."""
        print(f"[{time.strftime('%H:%M:%S')}] {self.address_string()} - {format % args}")

    def _require_auth(self) -> bool:
        """Returns True if authenticated, otherwise sends 401 and returns False."""
        if _check_auth(self):
            return True
        _send_401(self)
        return False

# The main request handler methods (do_GET, do_POST, do_PUT, do_DELETE) will go here.

    def do_GET(self):
        if not self._require_auth():
            return

        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        params = parse_qs(parsed.query)

        if path == "/transactions":
            page = int(params.get("page", [1])[0])
            limit = int(params.get("limit", [20])[0])
            txn_type = params.get("type", [None])[0]

            results = _transactions
            if txn_type:
                results = [t for t in results if t["transaction_type"] == txn_type]

            total = len(results)
            start = (page - 1) * limit
            end = start + limit
            _send_json(self, 200, {
                "page": page,
                "limit": limit,
                "total": total,
                "transactions": results[start:end],
            })
            return

  # allows searching transactions by party, type, or transaction ID using a query parameter 'q'.  
        if path == "/transactions/search":
            q = params.get("q", [""])[0].lower()
            results = [
                t for t in _transactions
                if q in t["party"].lower()
                or q in t["transaction_type"].lower()
                or q in t["transaction_id"].lower()
                or q in str(t["id"])
            ]
            _send_json(self, 200, {"query": q, "results": results, "count": len(results)})
            return

  # provides a benchmark endpoint to compare linear search vs dictionary lookup.
        if path == "/dsa/benchmark":
            results = benchmark(_transactions, iterations=50_000)
            results["note"] = (
                "Dictionary lookup uses a hash table (O(1) avg). "
                "Linear search is O(n). "
                "For even larger datasets, consider a B-tree index or binary search on sorted IDs."
            )
            _send_json(self, 200, results)
            return

     # allows fetching a single transaction by ID.
        m = re.fullmatch(r"/transactions/(\d+)", path)
        if m:
            tid = int(m.group(1))
            txn = dict_lookup(_index, tid)
            if txn:
                _send_json(self, 200, txn)
            else:
                _send_json(self, 404, {"error": f"Transaction {tid} not found."})
            return

        _send_json(self, 404, {"error": "Endpoint not found."})

# allows creating a new transaction. Expects JSON body with required fields: amount, transaction_type, party.
    def do_POST(self):
        if not self._require_auth():
            return

        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path != "/transactions":
            _send_json(self, 404, {"error": "Endpoint not found."})
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            _send_json(self, 400, {"error": "Invalid JSON body."})
            return
# Validate required fields
        required = ["amount", "transaction_type", "party"]
        missing = [f for f in required if f not in body]
        if missing:
            _send_json(self, 422, {"error": f"Missing fields: {missing}"})
            return

        global _next_id
        new_txn = {
            "id": _next_id,
            "address": body.get("address", ""),
            "date_ms": int(time.time() * 1000),
            "readable_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "body": body.get("body", ""),
            "transaction_type": body["transaction_type"],
            "amount": float(body["amount"]),
            "fee": float(body.get("fee", 0)),
            "balance_after": float(body.get("balance_after", 0)),
            "party": body["party"],
            "transaction_id": body.get("transaction_id", f"T{_next_id:04d}"),
        }
        _transactions.append(new_txn)
        _next_id += 1
        _refresh_index()
        _send_json(self, 201, new_txn)

#allows updating an existing transaction by ID.
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        m = re.fullmatch(r"/transactions/(\d+)", path)
        if not m:
            _send_json(self, 404, {"error": "Endpoint not found."})
            return

        tid = int(m.group(1))
        txn = dict_lookup(_index, tid)
        if not txn:
            _send_json(self, 404, {"error": f"Transaction {tid} not found."})
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            updates = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            _send_json(self, 400, {"error": "Invalid JSON body."})
            return

    
        updates.pop("id", None)
        txn.update(updates)
        _refresh_index()
        _send_json(self, 200, txn)

# allows deleting a transaction by ID
    def do_DELETE(self):
        if not self._require_auth():
            return

        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        m = re.fullmatch(r"/transactions/(\d+)", path)
        if not m:
            _send_json(self, 404, {"error": "Endpoint not found."})
            return

        tid = int(m.group(1))
        original_len = len(_transactions)
        _transactions[:] = [t for t in _transactions if t["id"] != tid]
        if len(_transactions) == original_len:
            _send_json(self, 404, {"error": f"Transaction {tid} not found."})
            return

        _refresh_index()
        _send_json(self, 200, {"message": f"Transaction {tid} deleted successfully."})

# The server entry point

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    server = HTTPServer(("0.0.0.0", port), MoMoHandler)
    print(f"MoMo API running on http://localhost:{port}")
    print(f"Loaded {len(_transactions)} transactions.")
    print("Auth  : admin / momo2024")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
