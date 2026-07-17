"""CLI for Markdown to PDF conversion."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from md_to_pdf.config import Config, load_config
from md_to_pdf.converter import convert_file, convert_batch

app = typer.Typer(
    name="md-to-pdf",
    help="Convert Markdown files to PDF",
    rich_markup_mode="rich",
    no_args_is_help=True,
)
console = Console()


@app.command()
def convert(
    input_file: Path = typer.Argument(..., help="Input markdown file", exists=True, readable=True),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output PDF file"),
    config_file: Optional[Path] = typer.Option(None, "-c", "--config", help="Config YAML file"),
    theme: Optional[str] = typer.Option(None, "-t", "--theme", help="Theme: light, dark, github"),
    page_size: Optional[str] = typer.Option(None, "--page-size", help="Page size: A4, Letter, Legal"),
):
    """Convert a single markdown file to PDF."""
    config = load_config(config_file)
    if theme:
        config.pdf.theme = theme
    if page_size:
        config.pdf.page_size = page_size

    output_path = output or input_file.with_suffix(".pdf")

    try:
        convert_file(input_file, output_path, config)
        console.print(f"[green]OK[/green] Converted [cyan]{input_file}[/cyan] -> [cyan]{output_path}[/cyan]")
    except Exception as e:
        console.print(f"[red]Error[/red]: {e}")
        raise typer.Exit(1)


@app.command()
def batch(
    input_dir: Path = typer.Argument(".", help="Input directory with markdown files"),
    output_dir: Optional[Path] = typer.Option(None, "-o", "--output-dir", help="Output directory"),
    pattern: str = typer.Option("*.md", "-p", "--pattern", help="File pattern"),
    config_file: Optional[Path] = typer.Option(None, "-c", "--config", help="Config YAML file"),
    theme: Optional[str] = typer.Option(None, "-t", "--theme", help="Theme: light, dark, github"),
):
    """Convert multiple markdown files to PDF."""
    config = load_config(config_file)
    if theme:
        config.pdf.theme = theme

    out_dir = output_dir or input_dir / "pdf"
    out_dir.mkdir(parents=True, exist_ok=True)

    md_files = list(input_dir.glob("*.md"))
    if not md_files:
        console.print("[yellow]No markdown files found[/yellow]")
        return

    for md_file in md_files:
        try:
            output_path = out_dir / f"{md_file.stem}.pdf"
            convert_file(md_file, output_path, config)
            console.print(f"[green]OK[/green] {md_file.name} -> {output_path.name}")
        except Exception as e:
            console.print(f"[red]Error[/red] {md_file.name}: {e}")

    console.print(f"[green]OK[/green] Converted {len(md_files)} files to [cyan]{out_dir}[/cyan]")


@app.command()
def init(
    path: Path = typer.Argument(Path("md-to-pdf.yaml"), help="Config file path"),
):
    """Create a sample configuration file."""
    from md_to_pdf.config import DEFAULT_CONFIG_YAML
    path.write_text(DEFAULT_CONFIG_YAML)
    console.print(f"[green]OK[/green] Created config at [cyan]{path}[/cyan]")


@app.command()
def version():
    """Show version."""
    from md_to_pdf import __version__
    console.print(f"md-to-pdf v{__version__}")


if __name__ == "__main__":
    app()