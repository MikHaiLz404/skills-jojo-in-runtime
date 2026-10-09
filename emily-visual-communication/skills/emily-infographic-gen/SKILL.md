---
name: emily-infographic-gen
description: Create infographics from supplied content and visual direction.
metadata:
  author: jojo - Ekaphop
  version: 1.0.0
  updated: 2026-04-16
  tags: [skill, infographic]
---
# Infographic Generator Skill

Generate professional infographics from text content using Pillow (pure Python, no AI needed).

## Quick Start

```bash
python3 scripts/create_infographic.py --title "Your Title" --data "Key1:Value1|Key2:Value2" --output output.png
```

## Usage

### CLI Mode
```bash
# Basic usage
python3 scripts/create_infographic.py --title "Project Milestone" --data "Task1:Done|Task2:In Progress" --output my_infographic.png

# Full options
python3 scripts/create_infographic.py \
  --title "Project Name" \
  --subtitle "Optional subtitle" \
  --data "Category1:Item1|Category2:Item2" \
  --theme dark \
  --output output.png \
  --width 1920 \
  --height 1080
```

### Arguments

| Flag | Default | Description |
|------|---------|-------------|
| `--title` | Required | Main title text |
| `--subtitle` | "" | Subtitle/description |
| `--data` | "" | Pipe-separated key:value pairs for items |
| `--theme` | `modern` | Theme: `modern` (white) or `dark` |
| `--accent` | auto | Primary accent color (hex without #) |
| `--output` | `output.png` | Output file path |
| `--width` | 1920 | Image width in pixels |
| `--height` | 1080 | Image height in pixels |

### Data Format

Use `|` to separate items, `:` to separate label and description:
```
"Main Task:Details|Secondary Task:More details|Gatekeeper:Boss fight"
```

## Programmatic Usage

```python
from infographic import create_infographic

# Simple
create_infographic("My Title", {"Item 1": "Desc", "Item 2": "Desc"})

# Full options
create_infographic(
    title="Project Milestone",
    subtitle="2026 Roadmap",
    items={"Task1": "Done", "Task2": "In Progress"},
    theme="dark",
    accent_color="22c55e",
    output_path="milestone.png"
)
```

## Themes

### Modern (Default)
- White/light gray background
- Clean flat design
- Color-coded bullets
- Sans-serif typography

### Dark
- Dark navy background
- Vibrant accent colors
- Glass-like cards
- High contrast text

## Output

Saves PNG to specified path. Default output is `infographic.png` in current directory.
