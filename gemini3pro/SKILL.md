---
name: gemini3pro
description: Query Google Gemini 3 Pro via grsai.com API for text generation and image analysis. Use for text generation, Q&A, summarization, code generation, creative writing, image analysis/vision, complex reasoning, and structured document generation. Triggers on "ask gemini", "use gemini", "query gemini", "analyze this image with gemini", or when a second opinion from another LLM is needed. Optionally accepts an image input for vision tasks.
---

# Gemini 3 Pro Text & Vision

## Usage

Run from the user's current working directory (do NOT cd into the skill directory):

**Text generation:**
```bash
uv run ~/.codex/skills/gemini3pro/scripts/query_gemini.py --prompt "your question" [--system-prompt "instructions"] [--output "response.md"] [--api-key KEY]
```

**Image analysis (vision):**
```bash
uv run ~/.codex/skills/gemini3pro/scripts/query_gemini.py --prompt "describe this image" --image "path/to/image.png" [--output "analysis.md"] [--api-key KEY]
```

## Parameters

- `--prompt` / `-p` (required): Question, task, or instructions
- `--image` / `-i`: Path to image for vision analysis (jpg, png, webp, gif)
- `--system-prompt` / `-s`: System instructions to set context/persona
- `--output` / `-o`: Save response to file (always prints to stdout too)
- `--api-key` / `-k`: API key (overrides `GRSAI_API_KEY` env var)

## API Key

Provide via `--api-key` argument or set `GRSAI_API_KEY` environment variable.

## Common Failures

- `Error: No API key provided.` → set `GRSAI_API_KEY` or pass `--api-key`
- `Error: Image not found:` → wrong path or unreadable file
- HTTP 401 → wrong or expired API key
- `Unexpected response format` → API error; check prompt for policy violations

## Output

Print the response to stdout. Optionally save to file with `--output`. Do not pipe output unless the user asks.

## Examples

```bash
uv run ~/.codex/skills/gemini3pro/scripts/query_gemini.py --prompt "Explain the difference between TCP and UDP in simple terms"
```

```bash
uv run ~/.codex/skills/gemini3pro/scripts/query_gemini.py --prompt "What objects are in this image?" --image "photo.jpg" --output "analysis.md"
```
