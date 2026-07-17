"""Markdown to PDF conversion using fpdf2 with built-in core fonts."""

from pathlib import Path
from typing import Optional

import markdown
from fpdf import FPDF

from md_to_pdf.config import Config, PDFConfig, load_config


class MarkdownPDF(FPDF):
    """Custom PDF class for Markdown rendering with built-in core fonts."""

    def __init__(self, config: PDFConfig):
        super().__init__()
        self.config = config
        self.set_auto_page_break(auto=True, margin=20)
        self.set_font("Helvetica", size=11)

    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def render_markdown(self, md_text: str):
        """Render markdown text to PDF using a simple HTML parser."""
        from html.parser import HTMLParser

        # Parse markdown to HTML
        md = markdown.Markdown(
            extensions=[
                "fenced_code",
                "tables",
                "toc",
                "codehilite",
                "attr_list",
                "md_in_html",
            ],
            extension_configs={
                "codehilite": {"css_class": "highlight", "use_pygments": True},
                "toc": {"title": "Table of Contents", "toc_depth": f"2-{self.config.toc_depth}"},
            },
        )
        html = md.convert(md_text)

        # Simple HTML to PDF parser
        class HTMLToPDFParser(HTMLParser):
            def __init__(self, pdf):
                super().__init__()
                self.pdf = pdf
                self._in_code = False
                self._in_pre = False
                self._in_blockquote = False
                self._in_table = False
                self._in_table_row = False
                self._in_table_cell = False
                self._table_cells = []
                self._table_rows = []
                self._list_stack = []
                self._list_counter = {}

            def handle_starttag(self, tag, attrs):
                if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                    level = int(tag[1])
                    sizes = {1: 20, 2: 16, 3: 14, 4: 12, 5: 11, 6: 10}
                    self.pdf.set_font("Helvetica", "B", sizes.get(level, 11))
                    self.pdf.ln(6 if level <= 2 else 4)
                elif tag == "p":
                    self.pdf.set_font("Helvetica", "", 11)
                    self.pdf.ln(2)
                elif tag in ("strong", "b"):
                    self.pdf.set_font("Helvetica", "B", self.pdf.font_size_pt)
                elif tag in ("em", "i"):
                    self.pdf.set_font("Helvetica", "I", self.pdf.font_size_pt)
                elif tag == "code" and not self._in_pre:
                    self._in_code = True
                    self.pdf.set_font("Courier", "", 9)
                    self.pdf.set_fill_color(240, 240, 240)
                elif tag == "pre":
                    self._in_pre = True
                    self.pdf.set_font("Courier", "", 9)
                    self.pdf.set_fill_color(30, 30, 30)
                    self.pdf.set_text_color(212, 212, 212)
                    self.pdf.ln(2)
                elif tag == "blockquote":
                    self._in_blockquote = True
                    self.pdf.set_x(self.pdf.l_margin + 10)
                elif tag == "table":
                    self._in_table = True
                    self._table_cells = []
                    self._table_rows = []
                elif tag == "tr":
                    self._in_table_row = True
                    self._table_cells = []
                elif tag in ("th", "td"):
                    self._in_table_cell = True
                elif tag == "ul":
                    self._list_stack.append("ul")
                    self._list_counter["ul"] = 0
                elif tag == "ol":
                    self._list_stack.append("ol")
                    self._list_counter["ol"] = 0
                elif tag == "li":
                    indent = len(self._list_stack) * 8
                    self.pdf.set_x(self.pdf.l_margin + indent)
                    if self._list_stack and self._list_stack[-1] == "ul":
                        self.pdf.cell(6, self.pdf.font_size, "- ")
                    else:
                        self._list_counter["ol"] = self._list_counter.get("ol", 0) + 1
                        self.pdf.cell(10, self.pdf.font_size, f"{self._list_counter['ol']}. ")

            def handle_endtag(self, tag):
                if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                    self.pdf.ln(4)
                    self.pdf.set_font("Helvetica", "", 11)
                elif tag == "p":
                    self.pdf.ln(4)
                elif tag in ("strong", "b", "em", "i"):
                    self.pdf.set_font("Helvetica", "", self.pdf.font_size_pt)
                elif tag == "code" and not self._in_pre:
                    self._in_code = False
                    self.pdf.set_font("Helvetica", "", 11)
                elif tag == "pre":
                    self._in_pre = False
                    self.pdf.set_font("Helvetica", "", 11)
                    self.pdf.set_text_color(0, 0, 0)
                    self.pdf.ln(4)
                elif tag == "blockquote":
                    self._in_blockquote = False
                    self.pdf.set_x(self.pdf.l_margin)
                elif tag == "table":
                    self._in_table = False
                    self._render_table()
                elif tag == "tr":
                    self._in_table_row = False
                    if self._table_cells:
                        self._table_rows.append(self._table_cells)
                        self._table_cells = []
                elif tag in ("th", "td"):
                    self._in_table_cell = False
                elif tag == "ul":
                    if self._list_stack:
                        self._list_stack.pop()
                elif tag == "ol":
                    if self._list_stack:
                        self._list_stack.pop()
                elif tag == "li":
                    self.pdf.ln(2)

            def handle_data(self, data):
                data = data.strip()
                if not data:
                    return
                avail_w = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
                if self._in_pre:
                    for line in data.split('\n'):
                        line = line.strip()
                        if line:
                            self.pdf.multi_cell(avail_w, 5, line, fill=True)
                            self.pdf.set_x(self.pdf.l_margin)
                elif self._in_code:
                    for line in data.split('\n'):
                        line = line.strip()
                        if line:
                            self.pdf.multi_cell(avail_w, 5, line, fill=True)
                            self.pdf.set_x(self.pdf.l_margin)
                elif self._in_blockquote:
                    self.pdf.multi_cell(avail_w - 10, 5, data)
                    self.pdf.set_x(self.pdf.l_margin)
                elif self._in_table_cell:
                    self._table_cells.append(data)
                else:
                    self.pdf.multi_cell(avail_w, 5, data)
                    self.pdf.set_x(self.pdf.l_margin)

            def _render_table(self):
                if not self._table_rows:
                    return
                avail_w = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
                for row_idx, row in enumerate(self._table_rows):
                    line = " | ".join(row)
                    self.pdf.set_font("Courier", "", 9)
                    self.pdf.multi_cell(avail_w, 5, line)
                self.pdf.ln(4)
                self._table_rows = []
                self._table_cells = []

        parser = HTMLToPDFParser(self)
        parser.feed(html)
        parser.close()


def convert_file(
    input_path: Path,
    output_path: Path,
    config: Optional[Config] = None,
) -> Path:
    """Convert a single markdown file to PDF."""
    if config is None:
        config = load_config()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    md_text = input_path.read_text(encoding="utf-8-sig")  # auto-strip BOM

    pdf = MarkdownPDF(config.pdf)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.render_markdown(md_text)
    pdf.output(output_path)

    return output_path


def convert_batch(
    input_dir: Path,
    output_dir: Path,
    config: Optional[Config] = None,
    pattern: str = "*.md",
) -> list[Path]:
    """Convert multiple markdown files to PDF."""
    if config is None:
        config = load_config()

    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for md_file in input_dir.glob(pattern):
        output_path = output_dir / f"{md_file.stem}.pdf"
        try:
            convert_file(md_file, output_path, config)
            results.append(output_path)
        except Exception as e:
            print(f"Error converting {md_file}: {e}")

    return results