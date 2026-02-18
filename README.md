# grsai.com Skills

Agent skills for [grsai.com](https://grsai.com) — AI image generation, video generation, and text/vision via Google's Gemini and Veo models.

## Available Skills

| Skill | Description |
|-------|-------------|
| [nano-banana-pro-grsai](plugins/nano-banana-pro-grsai/SKILL.md) | Generate or edit images (text-to-image, image-to-image; 1K/2K/4K) |
| [veo3-1](plugins/veo3-1/SKILL.md) | Generate videos with Google Veo 3.1 (720p/1080p/4K; 4/6/8s; 16:9 or 9:16) |
| [gemini3pro](plugins/gemini3pro/SKILL.md) | Text generation and image analysis via Google Gemini 3 Pro |

## Requirements

- `uv` — used to run skill scripts ([install](https://astral.sh/uv))
- `GRSAI_API_KEY` — API key from [grsai.com](https://grsai.com)

## Installation

### Claude Code

```bash
claude plugin marketplace add delneg/nano-banana-pro-skill-grsai-com
claude plugin install nano-banana-pro-grsai
claude plugin install veo3-1
claude plugin install gemini3pro
```

### Manual (any agent)

Copy the skill folders from `plugins/` to your agent's skills directory:

```bash
# Claude Code
cp -r plugins/* ~/.claude/skills/

# Codex
cp -r plugins/* ~/.codex/skills/

# OpenCode
cp -r plugins/* ~/.config/opencode/skill/

# Cursor
cp -r plugins/* ~/.cursor/skills/
```

### Cursor

1. Open Cursor Settings (`Cmd+Shift+J` / `Ctrl+Shift+J`)
2. Navigate to `Rules & Command` → `Project Rules` → Add Rule → Remote Rule (GitHub)
3. Enter: `https://github.com/delneg/nano-banana-pro-skill-grsai-com.git`

Skills are auto-discovered — the agent uses them automatically when your request matches their descriptions.

## Repository Structure

```
nano-banana-pro-skill-grsai-com/
└── plugins/
    ├── nano-banana-pro-grsai/
    │   ├── SKILL.md
    │   └── scripts/generate_image.py
    ├── veo3-1/
    │   ├── SKILL.md
    │   └── scripts/generate_video.py
    └── gemini3pro/
        ├── SKILL.md
        └── scripts/query_gemini.py
```

## License

MIT
