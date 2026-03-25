#!/usr/bin/env python3
"""Convert a constrained Markdown document into a styled DOCX file."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence

from docx import Document
from docx.document import Document as DocumentType
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.text import WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


FONT_NAME = "仿宋"
BODY_SIZE = Pt(16)
TITLE_SIZE = Pt(22)
FOOTER_SIZE = Pt(9)
FIRST_LINE_INDENT_PT = Pt(32)
INLINE_PATTERN = re.compile(r"(\*\*.+?\*\*|==.+?==)")


@dataclass
class Block:
    kind: str
    text: str
    marker: str = ""


@dataclass
class ParseResult:
    blocks: List[Block]
    warnings: List[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a limited Markdown document to a styled DOCX file."
    )
    parser.add_argument("input", help="Path to the input Markdown file.")
    parser.add_argument("output", help="Path to the output DOCX file.")
    parser.add_argument("--title", help="Override the title read from Markdown.")
    parser.add_argument("--footer", help="Footer text to write into the document.")
    parser.add_argument("--author", help="Document author metadata.")
    parser.add_argument("--subject", help="Document subject metadata.")
    return parser.parse_args()


def read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_blocks(markdown_text: str) -> ParseResult:
    lines = markdown_text.splitlines()
    blocks: List[Block] = []
    warnings: List[str] = []
    paragraph_lines: List[str] = []
    in_code_block = False
    code_block_lines: List[str] = []
    code_block_start_line: Optional[int] = None

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if not paragraph_lines:
            return
        text = " ".join(line.strip() for line in paragraph_lines).strip()
        if text:
            blocks.append(Block("paragraph", text))
        paragraph_lines = []

    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code_block:
                code_text = " ".join(code_block_lines).strip()
                if code_text:
                    blocks.append(Block("paragraph", code_text))
                warnings.append(
                    f"Line {code_block_start_line}: code block downgraded to plain paragraph text."
                )
                in_code_block = False
                code_block_lines = []
                code_block_start_line = None
            else:
                flush_paragraph()
                in_code_block = True
                code_block_start_line = lineno
            continue

        if in_code_block:
            if stripped:
                code_block_lines.append(stripped)
            continue

        if not stripped:
            flush_paragraph()
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            blocks.append(Block("paragraph", stripped.lstrip(">").strip()))
            warnings.append(f"Line {lineno}: blockquote downgraded to plain paragraph text.")
            continue

        if re.match(r"^\|.+\|$", stripped):
            flush_paragraph()
            blocks.append(Block("paragraph", stripped))
            warnings.append(f"Line {lineno}: table row downgraded to plain paragraph text.")
            continue

        if re.match(r"^\s{2,}([-*]|\d+\.)\s+.+$", line):
            flush_paragraph()
            blocks.append(Block("paragraph", stripped))
            warnings.append(f"Line {lineno}: nested list downgraded to plain paragraph text.")
            continue

        if stripped.startswith("# "):
            flush_paragraph()
            blocks.append(Block("title", stripped[2:].strip()))
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            blocks.append(Block("heading1", stripped[3:].strip()))
            continue

        if stripped.startswith("### "):
            flush_paragraph()
            blocks.append(Block("heading2", stripped[4:].strip()))
            continue

        bullet_match = re.match(r"^([-*])\s+(.+)$", stripped)
        if bullet_match:
            flush_paragraph()
            blocks.append(Block("list", bullet_match.group(2).strip(), marker="•"))
            continue

        ordered_match = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if ordered_match:
            flush_paragraph()
            marker = f"{ordered_match.group(1)}、"
            blocks.append(Block("list", ordered_match.group(2).strip(), marker=marker))
            continue

        paragraph_lines.append(stripped)

    flush_paragraph()
    if in_code_block:
        code_text = " ".join(code_block_lines).strip()
        if code_text:
            blocks.append(Block("paragraph", code_text))
        warnings.append(
            f"Line {code_block_start_line}: unclosed code block downgraded to plain paragraph text."
        )
    return ParseResult(blocks=blocks, warnings=warnings)


def ensure_rfonts(run) -> None:
    r_pr = run._r.get_or_add_rPr()
    r_fonts = r_pr.rFonts
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)
    for key in ("ascii", "hAnsi", "eastAsia"):
        r_fonts.set(qn(f"w:{key}"), FONT_NAME)


def set_run_font(run, size: Pt, *, bold: bool = False, highlight: bool = False) -> None:
    run.font.name = FONT_NAME
    run.font.size = size
    run.font.bold = bold
    if highlight:
        run.font.highlight_color = WD_COLOR_INDEX.YELLOW
    ensure_rfonts(run)


def set_snap_to_grid(paragraph, enabled: bool) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    snap = p_pr.find(qn("w:snapToGrid"))
    if snap is None:
        snap = OxmlElement("w:snapToGrid")
        p_pr.append(snap)
    snap.set(qn("w:val"), "1" if enabled else "0")


def add_inline_runs(paragraph, text: str, *, size: Pt, default_bold: bool = False) -> None:
    for part in INLINE_PATTERN.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            set_run_font(run, size, bold=True)
        elif part.startswith("==") and part.endswith("=="):
            run = paragraph.add_run(part[2:-2])
            set_run_font(run, size, bold=default_bold, highlight=True)
        else:
            run = paragraph.add_run(part)
            set_run_font(run, size, bold=default_bold)


def configure_document(document: DocumentType) -> None:
    section = document.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.18)
    section.right_margin = Cm(3.18)
    section.header_distance = Cm(1.5)
    section.footer_distance = Cm(1.75)


def write_title(document: DocumentType, title: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.first_line_indent = None
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(0)
    set_snap_to_grid(paragraph, False)
    add_inline_runs(paragraph, title, size=TITLE_SIZE, default_bold=True)


def write_heading(document: DocumentType, text: str, *, level: int) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.first_line_indent = FIRST_LINE_INDENT_PT if level == 1 else None
    set_snap_to_grid(paragraph, False)
    add_inline_runs(paragraph, text, size=BODY_SIZE, default_bold=True)


def write_paragraph(document: DocumentType, text: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.first_line_indent = FIRST_LINE_INDENT_PT
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(0)
    set_snap_to_grid(paragraph, False)
    add_inline_runs(paragraph, text, size=BODY_SIZE)


def write_list_item(document: DocumentType, text: str, marker: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.first_line_indent = FIRST_LINE_INDENT_PT
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(0)
    set_snap_to_grid(paragraph, False)
    add_inline_runs(paragraph, f"{marker} {text}", size=BODY_SIZE)


def set_footer(document: DocumentType, footer_text: str) -> None:
    for section in document.sections:
        paragraph = section.footer.paragraphs[0] if section.footer.paragraphs else section.footer.add_paragraph()
        if paragraph.runs:
            for run in list(paragraph.runs):
                run._element.getparent().remove(run._element)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = paragraph.add_run(footer_text)
        set_run_font(run, FOOTER_SIZE)


def apply_core_properties(document: DocumentType, *, author: Optional[str], subject: Optional[str]) -> None:
    if author:
        document.core_properties.author = author
    if subject:
        document.core_properties.subject = subject


def build_document(
    blocks: Sequence[Block],
    *,
    title_override: Optional[str] = None,
    footer: Optional[str] = None,
    author: Optional[str] = None,
    subject: Optional[str] = None,
) -> DocumentType:
    document = Document()
    configure_document(document)
    apply_core_properties(document, author=author, subject=subject)

    remaining_blocks = list(blocks)
    title = title_override
    if title is None and remaining_blocks and remaining_blocks[0].kind == "title":
        title = remaining_blocks.pop(0).text

    if title:
        write_title(document, title)

    for block in remaining_blocks:
        if block.kind == "title":
            write_heading(document, block.text, level=1)
        elif block.kind == "heading1":
            write_heading(document, block.text, level=1)
        elif block.kind == "heading2":
            write_heading(document, block.text, level=2)
        elif block.kind == "list":
            write_list_item(document, block.text, block.marker)
        else:
            write_paragraph(document, block.text)

    if footer:
        set_footer(document, footer)

    return document


def validate_paths(input_path: Path, output_path: Path) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.is_dir():
        raise IsADirectoryError(f"Input path is a directory: {input_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)


def emit_warnings(warnings: Sequence[str]) -> None:
    for warning in warnings:
        print(f"Warning: {warning}", file=sys.stderr)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    validate_paths(input_path, output_path)

    markdown_text = read_markdown(input_path)
    parse_result = parse_blocks(markdown_text)
    document = build_document(
        parse_result.blocks,
        title_override=args.title,
        footer=args.footer,
        author=args.author,
        subject=args.subject,
    )
    document.save(str(output_path))
    emit_warnings(parse_result.warnings)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
