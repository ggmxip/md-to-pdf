"""Configuration for Markdown to PDF conversion."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class PDFConfig(BaseModel):
    """PDF generation configuration."""

    page_size: Literal["A4", "Letter", "Legal"] = "A4"
    margin_top: str = "2cm"
    margin_right: str = "2cm"
    margin_bottom: str = "2cm"
    margin_left: str = "2cm"
    font_family: str = "system-ui, sans-serif"
    font_size: str = "12pt"
    line_height: str = "1.6"
    code_font_family: str = "monospace"
    code_font_size: str = "10pt"
    theme: Literal["light", "dark", "github"] = "light"
    include_toc: bool = False
    toc_depth: int = 3


class Config(BaseModel):
    """Application configuration."""

    pdf: PDFConfig = Field(default_factory=PDFConfig)
    input_dir: Path = Path(".")
    output_dir: Path = Path(".")
    css_file: Path | None = None


def load_config(config_path: Path | None = None) -> Config:
    """Load configuration from YAML file."""
    import yaml

    if config_path and config_path.exists():
        with config_path.open() as f:
            data = yaml.safe_load(f)
        return Config(**data)
    return Config()


DEFAULT_CONFIG_YAML = """# md-to-pdf configuration
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
"""