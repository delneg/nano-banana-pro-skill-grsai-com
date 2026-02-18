---
name: veo3.1
description: Generate videos with Google Veo 3.1 via grsai.com API. Use for video creation requests. Supports text-to-video; fast/pro quality; 720p/1080p/4K; 4, 6, or 8 second durations; 16:9 and 9:16 aspect ratios.
---

# Veo 3.1 Video Generation

Generate videos from text prompts using Google's Veo 3.1 model via the grsai.com API.

## Usage

Run the script using absolute path (do NOT cd to skill directory first):

**Generate video:**
```bash
uv run ~/.codex/skills/veo3.1/scripts/generate_video.py --prompt "your video description" --filename "output-name.mp4" [--model veo3.1-fast|veo3.1-pro|...] [--duration 4|6|8] [--aspect-ratio 16:9|9:16] [--api-key KEY]
```

**Important:** Always run from the user's current working directory so videos are saved where the user is working, not in the skill directory.

## Default Workflow (draft → final)

Goal: quick iteration with fast model before committing to pro quality.

- Draft (fast, 4s): quick preview
  - `uv run ~/.codex/skills/veo3.1/scripts/generate_video.py --prompt "<prompt>" --filename "yyyy-mm-dd-hh-mm-ss-draft.mp4" --model veo3.1-fast --duration 4`
- Final (pro, 8s): when prompt is locked
  - `uv run ~/.codex/skills/veo3.1/scripts/generate_video.py --prompt "<final prompt>" --filename "yyyy-mm-dd-hh-mm-ss-final.mp4" --model veo3.1-pro-4k --duration 8`

## Model Options

| Model | Quality | Resolution | Cost |
|-------|---------|------------|------|
| `veo3.1-fast` (default) | Fast | 720p | Lowest |
| `veo3.1-fast-1080p` | Fast | 1080p | Low |
| `veo3.1-fast-4k` | Fast | 4K | Medium |
| `veo3.1-pro` | Pro | 720p | Medium |
| `veo3.1-pro-1080p` | Pro | 1080p | High |
| `veo3.1-pro-4k` | Pro | 4K | Highest |

Map user requests to models:
- No mention → `veo3.1-fast`
- "fast", "quick preview", "draft" → `veo3.1-fast`
- "1080p", "HD" → `veo3.1-fast-1080p`
- "4K", "ultra" → `veo3.1-fast-4k`
- "high quality", "pro" → `veo3.1-pro`
- "high quality 4K", "best quality" → `veo3.1-pro-4k`

## Duration Options

- **4** seconds (good for drafts)
- **6** seconds
- **8** seconds (default, good for finals)

## Aspect Ratio Options

- **16:9** (default, landscape/widescreen)
- **9:16** (portrait, vertical/mobile)

## API Key

The script checks for API key in this order:
1. `--api-key` argument (use if user provided key in chat)
2. `GRSAI_API_KEY` environment variable

If neither is available, the script exits with an error message.

## Preflight + Common Failures

- Preflight:
  - `command -v uv` (must exist)
  - `test -n "$GRSAI_API_KEY"` (or pass `--api-key`)

- Common failures:
  - `Error: No API key provided.` → set `GRSAI_API_KEY` or pass `--api-key`
  - HTTP 401 → wrong or expired API key
  - `Generation failed:` → content moderation or invalid input; rephrase prompt
  - Timeout → try a faster model or shorter duration

## Filename Generation

Generate filenames with the pattern: `yyyy-mm-dd-hh-mm-ss-name.mp4`

**Format:** `{timestamp}-{descriptive-name}.mp4`
- Timestamp: Current date/time in format `yyyy-mm-dd-hh-mm-ss` (24-hour format)
- Name: Descriptive lowercase text with hyphens
- Keep the descriptive part concise (1-5 words typically)

Examples:
- Prompt "A golden sunset over mountains" → `2025-11-23-14-23-05-sunset-mountains.mp4`
- Prompt "Dancing robot in neon city" → `2025-11-23-15-30-12-dancing-robot-neon.mp4`

## Output

- Saves video to current directory (or specified path if filename includes directory)
- Script outputs the full path to the generated video
- **Do not read or open the video back** - just inform the user of the saved path

## Examples

**Quick draft:**
```bash
uv run ~/.codex/skills/veo3.1/scripts/generate_video.py --prompt "A golden sunset over mountain peaks with birds flying" --filename "2025-11-23-14-23-05-sunset-draft.mp4" --model veo3.1-fast --duration 4
```

**Final high-quality video:**
```bash
uv run ~/.codex/skills/veo3.1/scripts/generate_video.py --prompt "Close-up of waves crashing on a rocky shore, slow motion, cinematic" --filename "2025-11-23-15-30-12-ocean-waves-final.mp4" --model veo3.1-pro-4k --duration 8 --aspect-ratio 16:9
```

**Portrait/vertical video:**
```bash
uv run ~/.codex/skills/veo3.1/scripts/generate_video.py --prompt "Person walking through a rainy street at night, neon reflections" --filename "2025-11-23-16-00-00-rainy-street.mp4" --model veo3.1-fast-1080p --duration 6 --aspect-ratio 9:16
```
