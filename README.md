# md-to-pdf

Convert Markdown files to beautifully styled PDFs with a single command.

## Features

- **Multiple themes**: Light, Dark, GitHub-style
- **Batch conversion**: Process entire directories
- **Customizable**: Page size, margins, fonts, colors via YAML config
- **Table of contents**: Auto-generated with `--toc`
- **Syntax highlighting**: Code blocks with Pygments
- **GitHub-flavored Markdown**: Tables, task lists, footnotes

## Installation

```bash
# Using pipx (recommended)
pipx install md-to-pdf

# Or with uv
uv tool install md-to-pdf

# Or pip
pip install md-to-pdf
```

## Quick Start

```bash
# Single file
md-to-pdf convert README.md

# With theme
md-to-pdf convert README.md --theme dark

# With table of contents
md-to-pdf convert docs/guide.md --toc

# Batch convert directory
md-to-pdf convert docs/ -o pdfs/
```

## Configuration

Create a config file:

```bash
md-to-pdf init
```

Edit `md-to-pdf.yaml`:

```yaml
pdf:
  page_size: A4
  margin_top: "2cm"
  margin_right: "2cm"
  margin_bottom: "2cm"
  margin_left: "2cm"
  font_family: "system-ui, sans-serif"
  font_size: "12pt"
  line_height: "1.6"
  code_font_family: "monospace"
  code_font_size: "10pt"
  theme: light
  include_toc: false
  toc_depth: 3
```

## Themes

| Theme | Preview |
|-------|---------|
| `light` | Clean, professional |
| `dark` | Easy on eyes |
| `github` | GitHub-flavored |

```bash
md-to-pdf themes
```

## Requirements

- Python 3.10+
- System dependencies for WeasyPrint:
  - **Linux**: `sudo apt install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0`
  - **macOS**: `brew install pango gdk-pixbuf libffi`
  - **Windows**: Works out of the box

## License

MIT