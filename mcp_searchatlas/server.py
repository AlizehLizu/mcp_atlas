"""MCP server for Search Atlas SEO platform."""

import os
import httpx
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

BASE_URL = "https://api.searchatlas.com"

server = Server("searchatlas")


def get_headers() -> dict:
    token = os.environ.get("SEARCHATLAS_API_KEY")
    if not token:
        raise ValueError("SEARCHATLAS_API_KEY environment variable is not set.")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


# ── Tool definitions ──────────────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="keyword_research",
            description=(
                "Get keyword data from Search Atlas including search volume, "
                "difficulty, CPC, and related keywords."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "The keyword to research.",
                    },
                    "country": {
                        "type": "string",
                        "description": "Two-letter country code (e.g. 'us', 'gb'). Defaults to 'us'.",
                        "default": "us",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code (e.g. 'en'). Defaults to 'en'.",
                        "default": "en",
                    },
                },
                "required": ["keyword"],
            },
        ),
        types.Tool(
            name="get_backlinks",
            description=(
                "Retrieve backlink data for a domain or URL, including referring "
                "domains, anchor texts, and link authority metrics."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "The domain or URL to get backlinks for (e.g. 'example.com').",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of backlinks to return (default 20, max 100).",
                        "default": 20,
                    },
                },
                "required": ["target"],
            },
        ),
        types.Tool(
            name="site_audit",
            description=(
                "Run an SEO site audit to identify technical issues such as broken "
                "links, missing meta tags, slow pages, and crawl errors."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "The domain to audit (e.g. 'example.com').",
                    },
                },
                "required": ["domain"],
            },
        ),
        types.Tool(
            name="rank_tracker",
            description=(
                "Check the current search engine ranking positions for a domain "
                "and a list of keywords."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "The domain to track rankings for.",
                    },
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of keywords to check rankings for.",
                    },
                    "country": {
                        "type": "string",
                        "description": "Two-letter country code. Defaults to 'us'.",
                        "default": "us",
                    },
                },
                "required": ["domain", "keywords"],
            },
        ),
        types.Tool(
            name="competitor_analysis",
            description=(
                "Analyse a competitor domain to see their top keywords, estimated "
                "organic traffic, and top-ranking pages."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "The competitor domain to analyse.",
                    },
                    "country": {
                        "type": "string",
                        "description": "Two-letter country code. Defaults to 'us'.",
                        "default": "us",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top keywords to return (default 20).",
                        "default": 20,
                    },
                },
                "required": ["domain"],
            },
        ),
        types.Tool(
            name="content_optimizer",
            description=(
                "Get on-page SEO recommendations for a piece of content targeting "
                "a specific keyword."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "The target keyword for the content.",
                    },
                    "url": {
                        "type": "string",
                        "description": "Optional URL of an existing page to analyse.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Optional raw content text to analyse.",
                    },
                },
                "required": ["keyword"],
            },
        ),
        types.Tool(
            name="knowledge_graph",
            description=(
                "Query the Search Atlas knowledge graph for entity data related to "
                "a topic or brand."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity": {
                        "type": "string",
                        "description": "The entity or topic to query.",
                    },
                },
                "required": ["entity"],
            },
        ),
    ]


# ── Tool call handler ─────────────────────────────────────────────────────────

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        headers = get_headers()
    except ValueError as e:
        return [types.TextContent(type="text", text=str(e))]

    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=30) as client:
        try:
            result = await _dispatch(client, name, arguments)
        except httpx.HTTPStatusError as e:
            result = {
                "error": f"HTTP {e.response.status_code}",
                "detail": e.response.text,
            }
        except httpx.RequestError as e:
            result = {"error": "Request failed", "detail": str(e)}

    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def _dispatch(client: httpx.AsyncClient, name: str, args: dict) -> dict:
    if name == "keyword_research":
        resp = await client.post(
            "/api/v1/keywords/research/",
            json={
                "keyword": args["keyword"],
                "country": args.get("country", "us"),
                "language": args.get("language", "en"),
            },
        )
        resp.raise_for_status()
        return resp.json()

    elif name == "get_backlinks":
        resp = await client.get(
            "/api/v1/backlinks/",
            params={"target": args["target"], "limit": args.get("limit", 20)},
        )
        resp.raise_for_status()
        return resp.json()

    elif name == "site_audit":
        resp = await client.post(
            "/api/v1/site-audit/",
            json={"domain": args["domain"]},
        )
        resp.raise_for_status()
        return resp.json()

    elif name == "rank_tracker":
        resp = await client.post(
            "/api/v1/rank-tracker/",
            json={
                "domain": args["domain"],
                "keywords": args["keywords"],
                "country": args.get("country", "us"),
            },
        )
        resp.raise_for_status()
        return resp.json()

    elif name == "competitor_analysis":
        resp = await client.get(
            "/api/v1/competitors/",
            params={
                "domain": args["domain"],
                "country": args.get("country", "us"),
                "limit": args.get("limit", 20),
            },
        )
        resp.raise_for_status()
        return resp.json()

    elif name == "content_optimizer":
        payload: dict = {"keyword": args["keyword"]}
        if "url" in args:
            payload["url"] = args["url"]
        if "content" in args:
            payload["content"] = args["content"]
        resp = await client.post("/api/v1/content-optimizer/", json=payload)
        resp.raise_for_status()
        return resp.json()

    elif name == "knowledge_graph":
        resp = await client.get(
            "/api/v1/knowledge-graph/",
            params={"entity": args["entity"]},
        )
        resp.raise_for_status()
        return resp.json()

    else:
        return {"error": f"Unknown tool: {name}"}


# ── Entry point ───────────────────────────────────────────────────────────────

async def _main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main():
    import asyncio
    asyncio.run(_main())


if __name__ == "__main__":
    main()
