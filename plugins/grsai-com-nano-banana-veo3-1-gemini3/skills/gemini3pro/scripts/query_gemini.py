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
import time
import urllib.error
import urllib.request
from pathlib import Path


GRSAI_CHAT_URL = "https://grsaiapi.com/v1/chat/completions"
MODEL = "gemini-3-pro"

REQUEST_TIMEOUT = 120   # seconds — Gemini can be slow on long tasks
MAX_RETRIES = 3
RETRY_DELAY = 4.0


class TransientError(RuntimeError):
    """Raised for transient errors that are worth retrying (rate limits, server errors, timeouts)."""


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
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        if e.code == 401:
            raise RuntimeError(f"Unauthorized (HTTP 401): check your API key. Details: {body_text}")
        if e.code == 429:
            raise TransientError(f"HTTP 429: too many requests. Details: {body_text}")
        if e.code >= 500:
            raise TransientError(f"HTTP {e.code}: {body_text}")
        raise RuntimeError(f"HTTP {e.code}: {body_text}")
    except urllib.error.URLError as e:
        raise TransientError(f"Could not connect to {url}: {e.reason}")
    except TimeoutError:
        raise TransientError(f"Request timed out after {REQUEST_TIMEOUT}s")


def query_with_retry(payload: dict, api_key: str) -> dict:
    """Call the API with exponential backoff retry on transient errors."""
    delay = RETRY_DELAY
    last_error: Exception = RuntimeError("No attempts made")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return http_post(GRSAI_CHAT_URL, payload, api_key)
        except TransientError as e:
            last_error = e
            if attempt < MAX_RETRIES:
                print(f"Attempt {attempt} failed (will retry in {delay:.0f}s): {e}", file=sys.stderr)
                time.sleep(delay)
                delay = min(delay * 2, 30)
        except RuntimeError:
            raise  # Permanent error, don't retry

    raise last_error


def load_image_as_base64(image_path: str) -> tuple[str, str]:
    """Load image file and return (mime_type, base64_data)."""
    path = Path(image_path)
    if not path.exists():
        print(f"Error: Image not found: {image_path}", file=sys.stderr)
        sys.exit(1)
    if not path.is_file():
        print(f"Error: Not a file: {image_path}", file=sys.stderr)
        sys.exit(1)

    ext = path.suffix.lower().lstrip(".")
    mime_map = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp", "gif": "gif"}
    mime = mime_map.get(ext)
    if not mime:
        print(f"Error: Unsupported image format '{ext}'. Use jpg, png, webp, or gif.", file=sys.stderr)
        sys.exit(1)

    try:
        img_data = path.read_bytes()
    except OSError as e:
        print(f"Error reading image: {e}", file=sys.stderr)
        sys.exit(1)

    size_kb = len(img_data) // 1024
    print(f"Loaded image: {image_path} ({size_kb} KB, {ext.upper()})")
    return f"image/{mime}", base64.b64encode(img_data).decode("utf-8")


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
        print("Set GRSAI_API_KEY environment variable or pass --api-key", file=sys.stderr)
        sys.exit(1)

    # Build message content
    if args.image:
        mime_type, b64_data = load_image_as_base64(args.image)
        content = [
            {"type": "text", "text": args.prompt},
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64_data}"}},
        ]
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
    print(f"Querying {MODEL} ({mode})...")

    try:
        response = query_with_retry(payload, api_key)
    except (RuntimeError, TransientError) as e:
        print(f"\nRequest failed: {e}", file=sys.stderr)
        sys.exit(1)

    choices = response.get("choices")
    if not choices:
        print(f"Error: Unexpected response format — no 'choices' field: {response}", file=sys.stderr)
        sys.exit(1)

    message = choices[0].get("message", {})
    text = message.get("content")
    if text is None:
        print(f"Error: No content in response message: {message}", file=sys.stderr)
        sys.exit(1)

    usage = response.get("usage", {})
    if usage:
        total_tokens = usage.get("total_tokens", "?")
        print(f"Tokens used: {total_tokens}")

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
