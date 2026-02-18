#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Generate text or analyze images using grsai.com Gemini 3 Pro API.

Usage:
    uv run query_gemini.py --prompt "your question" [--image "path/to/image.png"] [--output "response.md"] [--api-key KEY]
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


GRSAI_CHAT_URL = "https://grsaiapi.com/v1/chat/completions"
MODEL = "gemini-3-pro"


def get_api_key(provided_key: str | None) -> str | None:
    if provided_key:
        return provided_key
    return os.environ.get("GRSAI_API_KEY")


def http_post(url: str, data: dict, api_key: str) -> dict:
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(
        description="Generate text or analyze images using grsai.com Gemini 3 Pro API"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Text prompt or question")
    parser.add_argument("--image", "-i", help="Optional path to image for vision analysis (jpg, png, webp, gif)")
    parser.add_argument("--system-prompt", "-s", help="Optional system instructions")
    parser.add_argument("--output", "-o", help="Optional file path to save the response")
    parser.add_argument("--api-key", "-k", help="grsai API key (overrides GRSAI_API_KEY env var)")

    args = parser.parse_args()

    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set GRSAI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    # Build message content
    if args.image:
        image_path = Path(args.image)
        if not image_path.exists():
            print(f"Error: Image not found: {args.image}", file=sys.stderr)
            sys.exit(1)
        img_data = image_path.read_bytes()
        ext = image_path.suffix.lower().lstrip(".")
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp", "gif": "gif"}.get(ext, "jpeg")
        b64 = base64.b64encode(img_data).decode("utf-8")
        content = [
            {"type": "text", "text": args.prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/{mime};base64,{b64}"}},
        ]
        print(f"Loaded image: {args.image}")
    else:
        content = args.prompt

    messages = []
    if args.system_prompt:
        messages.append({"role": "system", "content": args.system_prompt})
    messages.append({"role": "user", "content": content})

    payload = {
        "model": MODEL,
        "messages": messages,
    }

    mode = "vision" if args.image else "text"
    print(f"Querying Gemini 3 Pro ({mode})...")

    try:
        response = http_post(GRSAI_CHAT_URL, payload, api_key)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code} error: {body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)

    if "choices" not in response or not response["choices"]:
        print(f"Unexpected response format: {response}", file=sys.stderr)
        sys.exit(1)

    text = response["choices"][0]["message"]["content"]

    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
        print(f"\nResponse saved: {output_path.resolve()}")


if __name__ == "__main__":
    main()
