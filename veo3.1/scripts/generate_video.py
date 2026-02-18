#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Generate videos using grsai.com Veo 3.1 API.

Usage:
    uv run generate_video.py --prompt "your video description" --filename "output.mp4" [--model veo3.1-fast] [--duration 8] [--api-key KEY]
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


GRSAI_VIDEO_URL = "https://grsaiapi.com/v1/video/veo"
GRSAI_RESULT_URL = "https://grsaiapi.com/v1/draw/result"

AVAILABLE_MODELS = [
    "veo3.1-fast",
    "veo3.1-fast-1080p",
    "veo3.1-fast-4k",
    "veo3.1-pro",
    "veo3.1-pro-1080p",
    "veo3.1-pro-4k",
]

PERMANENT_KEYWORDS = ("moderation", "nsfw", "invalid", "unauthorized", "forbidden", "not exist")


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
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def is_permanent_error(msg: str) -> bool:
    msg_lower = msg.lower()
    return any(kw in msg_lower for kw in PERMANENT_KEYWORDS)


def submit_task(payload: dict, api_key: str) -> str:
    """Submit a generation task, return task_id."""
    response = http_post(GRSAI_VIDEO_URL, payload, api_key)
    if response.get("code") != 0:
        raise RuntimeError(response.get("msg", "Unknown error"))
    return response["data"]["id"]


def poll_result(task_id: str, api_key: str, poll_interval: float = 5.0, timeout: int = 600) -> dict:
    """Poll for task result until succeeded, failed, or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = http_post(GRSAI_RESULT_URL, {"id": task_id}, api_key)
        if result.get("code") != 0:
            raise RuntimeError(f"Result API error: {result.get('msg')}")
        data = result["data"]
        status = data.get("status")
        progress = data.get("progress", 0)
        print(f"  Progress: {progress}% ({status})")
        if status == "succeeded":
            return data
        if status == "failed":
            reason = (data.get("failure_reason", "") + " " + data.get("error", "")).strip()
            raise RuntimeError(reason or "unknown failure")
        time.sleep(poll_interval)
    raise TimeoutError(f"Generation timed out after {timeout}s")


def try_generate(payload: dict, api_key: str, max_retries: int = 3) -> dict:
    """Try to generate with retries on transient errors."""
    delay = 5.0
    last_error: Exception = RuntimeError("no attempts made")

    for attempt in range(1, max_retries + 1):
        try:
            model = payload["model"]
            print(f"[{model}] Attempt {attempt}/{max_retries}: submitting task...")
            task_id = submit_task(payload, api_key)
            print(f"[{model}] Task created: {task_id}")
            return poll_result(task_id, api_key)

        except TimeoutError as e:
            last_error = e
            print(f"Attempt {attempt} timed out: {e}")

        except RuntimeError as e:
            msg = str(e)
            last_error = e
            if is_permanent_error(msg):
                print(f"Permanent error (will not retry): {msg}")
                raise
            print(f"Attempt {attempt} failed: {msg}")

        if attempt < max_retries:
            print(f"Retrying in {delay:.0f}s...")
            time.sleep(delay)
            delay = min(delay * 2, 60)

    raise last_error


def main():
    parser = argparse.ArgumentParser(
        description="Generate videos using grsai.com Veo 3.1 API"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Video description/prompt")
    parser.add_argument("--filename", "-f", required=True, help="Output filename (e.g., output.mp4)")
    parser.add_argument(
        "--model", "-m",
        choices=AVAILABLE_MODELS,
        default="veo3.1-fast",
        help="Model to use (default: veo3.1-fast)",
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        choices=[4, 6, 8],
        default=8,
        help="Video duration in seconds: 4, 6, or 8 (default: 8)",
    )
    parser.add_argument(
        "--aspect-ratio", "-a",
        choices=["16:9", "9:16"],
        default="16:9",
        help="Aspect ratio: 16:9 (default, landscape) or 9:16 (portrait)",
    )
    parser.add_argument("--api-key", "-k", help="grsai API key (overrides GRSAI_API_KEY env var)")

    args = parser.parse_args()

    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set GRSAI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "model": args.model,
        "prompt": args.prompt,
        "durationSeconds": args.duration,
        "aspectRatio": args.aspect_ratio,
        "webHook": "-1",
    }

    print(f"Generating video — model={args.model}, duration={args.duration}s, aspect={args.aspect_ratio}")

    try:
        result = try_generate(payload, api_key)
    except (RuntimeError, TimeoutError) as e:
        print(f"Generation failed: {e}", file=sys.stderr)
        sys.exit(1)

    video_url = result["results"][0]["url"]

    print("Downloading video...")
    try:
        with urllib.request.urlopen(video_url, timeout=180) as resp:
            output_path.write_bytes(resp.read())
    except Exception as e:
        print(f"Error downloading video: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nVideo saved: {output_path.resolve()}")


if __name__ == "__main__":
    main()
