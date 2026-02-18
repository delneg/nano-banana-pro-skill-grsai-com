---
name: gemini3pro
description: Generate text and analyze images with Google Gemini 3 Pro via grsai.com API. Use for text generation, Q&A, summarization, code generation, creative writing, and image analysis/vision tasks. Optionally accepts an image input for vision tasks.
---

# Gemini 3 Pro Text & Vision

Generate text responses or analyze images using Google Gemini 3 Pro via the grsai.com API.

## Usage

Run the script using absolute path (do NOT cd to skill directory first):

**Text generation:**
```bash
uv run ~/.codex/skills/gemini3pro/scripts/query_gemini.py --prompt "your question or task" [--system-prompt "optional system instructions"] [--output "response.md"] [--api-key KEY]
```

**Image analysis (vision):**
```bash
uv run ~/.codex/skills/gemini3pro/scripts/query_gemini.py --prompt "describe this image" --image "path/to/image.png" [--output "analysis.md"] [--api-key KEY]
```

**Important:** Always run from the user's current working directory so output files are saved where the user is working.

## When to Use

- Text generation, creative writing, Q&A, summarization
- Code generation, code review, debugging explanations
- Image analysis, description, or interpretation (vision)
- Complex reasoning and multi-step tasks
- Structured document generation (reports, outlines, plans)

## Parameters

- `--prompt` / `-p` (required): Your question, task, or instructions
- `--image` / `-i`: Path to image file for vision analysis (jpg, png, webp, gif)
- `--system-prompt` / `-s`: Optional system instructions to set context/persona
- `--output` / `-o`: Save the response to this file path (optional; prints to stdout always)
- `--api-key` / `-k`: API key (overrides GRSAI_API_KEY env var)

## API Key

The script checks for API key in this order:
1. `--api-key` argument (use if user provided key in chat)
2. `GRSAI_API_KEY` environment variable

If neither is available, the script exits with an error message.

## Preflight + Common Failures

- Preflight:
  - `command -v uv` (must exist)
  - `test -n "$GRSAI_API_KEY"` (or pass `--api-key`)
  - If vision: `test -f "path/to/image.png"`

- Common failures:
  - `Error: No API key provided.` → set `GRSAI_API_KEY` or pass `--api-key`
  - `Error: Image not found:` → wrong path or unreadable file
  - HTTP 401 → wrong or expired API key
  - `Unexpected response format` → API error; check prompt for policy violations

## Output

- Prints the response to stdout with separator lines
- Optionally saves to file with `--output`; does not overwrite without confirmation
- Do not pipe the output to other commands unless the user explicitly asks

## Examples

**Simple Q&A:**
```bash
uv run ~/.codex/skills/gemini3pro/scripts/query_gemini.py --prompt "Explain the difference between TCP and UDP in simple terms"
```

**Creative writing with system prompt:**
```bash
uv run ~/.codex/skills/gemini3pro/scripts/query_gemini.py --prompt "Write a short story about a lighthouse keeper who discovers a message in a bottle" --system-prompt "You are a literary fiction author with a minimalist style" --output "story.md"
```

**Code review:**
```bash
uv run ~/.codex/skills/gemini3pro/scripts/query_gemini.py --prompt "Review this Python code for bugs and suggest improvements" --image "code-screenshot.png"
```

**Image analysis:**
```bash
uv run ~/.codex/skills/gemini3pro/scripts/query_gemini.py --prompt "What objects are in this image? What mood does it convey?" --image "photo.jpg"
```

**Document generation saved to file:**
```bash
uv run ~/.codex/skills/gemini3pro/scripts/query_gemini.py --prompt "Write a comprehensive README for a Python CLI tool that converts CSV to JSON" --output "README.md"
```
