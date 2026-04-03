"""Stdio-to-HTTP proxy for the Search Atlas remote MCP server."""

import sys
import os
import json
import httpx

API_KEY = os.environ.get("SEARCHATLAS_API_KEY", "")
REMOTE_URL = "https://mcp.searchatlas.com/api/v1/mcp"


def main():
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer

    with httpx.Client(timeout=60) as client:
        for line in stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
                response = client.post(
                    REMOTE_URL,
                    json=request,
                    headers={
                        "Content-Type": "application/json",
                        "X-API-KEY": API_KEY,
                    },
                )
                result = response.json()
            except Exception as e:
                result = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": str(e)},
                }
            stdout.write((json.dumps(result) + "\n").encode())
            stdout.flush()


if __name__ == "__main__":
    main()
