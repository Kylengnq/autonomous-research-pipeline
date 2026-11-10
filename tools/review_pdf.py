#!/usr/bin/env python3
"""Render review documents to PDF for the author (stdlib only, xelatex).

Author decision: **anything the pipeline hands a human to decide on
is delivered as a PDF, never as Markdown.** A checkpoint that presents a slate,
a proposal, a pre-registration or a decision letter presents PDF paths; the
Markdown stays the machine-readable source that the skills read and the ledger
traces.

The reason is the reading, not the format. A gate document is read once,
carefully, by someone deciding something, often away from the terminal. Markdown
in a terminal renders tables as pipes, hides the structure the document was
written to carry, and cannot be annotated or carried out of the session.

No new dependency: this converts Markdown to LaTeX and compiles with the
`xelatex` already installed. pandoc is not required and is not installed. The
converter deliberately covers the subset the pipeline actually writes -- ATX
headings, GFM pipe tables, fenced and inline code, bullet and numbered lists,
blockquotes, rules, links, bold and italic, and YAML front matter -- and escapes
everything else rather than guessing.

Usage:
    python3 review_pdf.py FILE.md [FILE.md ...]        # one PDF per file
    python3 review_pdf.py --packet G1.pdf A.md B.md    # one packet, cover page
    python3 review_pdf.py --outdir DIR FILE.md
    python3 review_pdf.py --title "G1 slate" FILE.md

Exit 0 when every requested PDF was produced, 1 otherwise. Prints one line per
PDF written, so a caller can hand the paths straight to the author.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


# Glyphs the pipeline's prose uses that a default TeX font may not carry.
# Mapped before escaping so the PDF shows the mark rather than a missing glyph.
GLYPHS = {
    "\u2014": "---", "\u2013": "--", "\u2018": "`", "\u2019": "'",
    "\u201c": "``", "\u201d": "''", "\u2026": r"\ldots{}",
    "\u2192": r"$\rightarrow$", "\u2190": r"$\leftarrow$",
    "\u21d2": r"$\Rightarrow$", "\u2264": r"$\leq$", "\u2265": r"$\geq$",
    "\u2260": r"$\neq$", "\u00d7": r"$\times$", "\u00b1": r"$\pm$",
    "\u2248": r"$\approx$", "\u00a0": "~",
    "\u2713": r"\checkmark{}", "\u2717": r"$\times$", "\u2022": r"$\bullet$",
    "\u00a7": r"\S{}", "\u2019": "'",
}

ESCAPES = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}

HEADING_CMDS = ["section", "subsection", "subsubsection", "paragraph", "subparagraph"]


def latex_escape(text: str) -> str:
    """Escape LaTeX specials, then restore the glyph substitutions.

    Order matters and getting it wrong is silent. Substituting glyphs first
    inserts LaTeX commands, whose backslashes and dollar signs the escaper then
    escapes in turn, so a section sign arrives on the page as a literal
    \\S{} and an arrow as $\\rightarrow$. Both render, neither errors, and
    only reading the PDF finds it. So the glyphs go out as sentinels that
    survive escaping and come back afterwards."""
    order = [g for g in GLYPHS if g in text]
    for i, glyph in enumerate(order):
        text = text.replace(glyph, f"\x02{i}\x02")
    text = "".join(ESCAPES.get(ch, ch) for ch in text)
    for i, glyph in enumerate(order):
        text = text.replace(f"\x02{i}\x02", GLYPHS[glyph])
    return text


def inline(text: str) -> str:
    """Inline markup, applied to already-unescaped source text.

    Code spans are pulled out first and restored last, so markup characters
    inside them are never interpreted."""
    spans: list[str] = []

    def stash_code(m: re.Match) -> str:
        spans.append(m.group(1))
        return f"\x00{len(spans) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash_code, text)

    # Links before escaping, so the URL survives as an argument.
    links: list[tuple[str, str]] = []

    def stash_link(m: re.Match) -> str:
        links.append((m.group(1), m.group(2)))
        return f"\x01{len(links) - 1}\x01"

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", stash_link, text)

    text = latex_escape(text)

    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"\\textbf{\\emph{\1}}", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"\\emph{\1}", text)

    for i, (label, url) in enumerate(links):
        safe_url = url.replace("%", "\\%").replace("#", "\\#")
        text = text.replace(
            f"\x01{i}\x01",
            "\\href{" + safe_url + "}{" + latex_escape(label) + "}",
        )
    for i, code in enumerate(spans):
        text = text.replace(f"\x00{i}\x00", f"\\texttt{{{latex_escape(code)}}}")
    return text


def split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def is_separator(line: str) -> bool:
    return bool(re.fullmatch(r"\s*\|?[\s:|-]+\|?\s*", line)) and "-" in line


def render_table(rows: list[list[str]], aligns: list[str]) -> str:
    """GFM pipe table as a booktabs longtable.

    Column widths are proportional to the longest cell, because these tables are
    mostly prose (a rationale column beside a one-word verdict column) and equal
    widths make them unreadable."""
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    aligns = (aligns + ["l"] * ncol)[:ncol]

    weights = []
    for c in range(ncol):
        longest = max(len(r[c]) for r in rows) or 1
        weights.append(min(max(longest, 6), 60))
    total = sum(weights)
    # 0.96 leaves room for the inter-column padding longtable adds.
    spec = "".join(
        f">{{\\raggedright\\arraybackslash}}p{{{0.96 * w / total:.3f}\\linewidth}}"
        for w in weights
    )

    head = " & ".join(f"\\textbf{{{inline(c)}}}" for c in rows[0]) + r" \\"
    body = [" & ".join(inline(c) for c in r) + r" \\" for r in rows[1:]]

    return "\n".join([
        r"\begingroup\footnotesize",
        f"\\begin{{longtable}}{{{spec}}}",
        r"\toprule", head, r"\midrule\endfirsthead",
        r"\toprule", head, r"\midrule\endhead",
        r"\bottomrule\endfoot",
        *body,
        r"\end{longtable}",
        r"\endgroup",
    ])


def parse_front_matter(lines: list[str]) -> tuple[dict, list[str]]:
    if not lines or lines[0].strip() != "---":
        return {}, lines
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            meta = {}
            for line in lines[1:i]:
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            return meta, lines[i + 1:]
    return {}, lines


def convert(md: str, base_level: int = 0, drop_title: str = None) -> tuple[str, dict]:
    """Markdown to a LaTeX body. `base_level` demotes headings, so several
    documents can be bound into one packet under their own part headings."""
    lines = md.replace("\r\n", "\n").split("\n")
    meta, lines = parse_front_matter(lines)
    out: list[str] = []
    i = 0
    list_stack: list[str] = []

    def close_lists(to_depth: int = 0) -> None:
        while len(list_stack) > to_depth:
            out.append(r"\end{" + list_stack.pop() + "}")

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            # A blank line inside a list is a paragraph break within the item,
            # not the end of the list. Closing here and reopening on the next
            # bullet is what produced skipped nesting levels.
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            continues = (
                j < len(lines)
                and list_stack
                and (
                    re.match(r"^(\s*)([-*+]|\d+[.)])\s+", lines[j])
                    or len(lines[j]) - len(lines[j].lstrip()) >= 2
                )
            )
            if not continues:
                close_lists()
            out.append("")
            i += 1
            continue

        # fenced code
        if stripped.startswith("```"):
            close_lists()
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append(r"\begin{quote}\begingroup\footnotesize\begin{verbatim}")
            out.extend(b.replace("\t", "    ") for b in buf)
            out.append(r"\end{verbatim}\endgroup\end{quote}")
            continue

        # heading
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            close_lists()
            # The cover already carries the document title; repeating it as the
            # first heading reads as a mistake in a printed document.
            if (drop_title is not None and len(m.group(1)) == 1
                    and m.group(2).strip() == drop_title.strip()):
                drop_title = None
                i += 1
                continue
            level = min(len(m.group(1)) - 1 + base_level, len(HEADING_CMDS) - 1)
            out.append(f"\\{HEADING_CMDS[level]}*{{{inline(m.group(2))}}}")
            out.append(f"\\addcontentsline{{toc}}{{{HEADING_CMDS[min(level, 2)]}}}"
                       f"{{{inline(m.group(2))}}}")
            i += 1
            continue

        # rule
        if re.fullmatch(r"(\*\s*){3,}|(-\s*){3,}|(_\s*){3,}", stripped):
            close_lists()
            out.append(r"\medskip\hrule\medskip")
            i += 1
            continue

        # table
        if "|" in stripped and i + 1 < len(lines) and is_separator(lines[i + 1]):
            close_lists()
            header = split_row(stripped)
            aligns = []
            for cell in split_row(lines[i + 1]):
                aligns.append("c" if cell.startswith(":") and cell.endswith(":")
                              else "r" if cell.endswith(":") else "l")
            rows = [header]
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append(split_row(lines[i]))
                i += 1
            out.append(render_table(rows, aligns))
            continue

        # blockquote
        if stripped.startswith(">"):
            close_lists()
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            inner, _ = convert("\n".join(buf), base_level)
            out.append(r"\begin{quote}" + "\n" + inner + "\n" + r"\end{quote}")
            continue

        # lists
        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", line)
        if m:
            indent, marker, content = m.group(1), m.group(2), m.group(3)
            # Clamp to one level deeper than the open stack. A source that
            # jumps from no list straight to an indented bullet would otherwise
            # emit two \begin lines with no \item between them, which is a
            # LaTeX error ("missing \item") rather than a rendering quirk.
            depth = min(len(indent) // 2 + 1, len(list_stack) + 1)
            env = "enumerate" if re.match(r"\d", marker) else "itemize"
            while len(list_stack) > depth:
                out.append(r"\end{" + list_stack.pop() + "}")
            if len(list_stack) < depth:
                while len(list_stack) < depth:
                    out.append(r"\begin{" + env + "}")
                    list_stack.append(env)
            elif list_stack and list_stack[-1] != env:
                out.append(r"\end{" + list_stack.pop() + "}")
                out.append(r"\begin{" + env + "}")
                list_stack.append(env)
            out.append(r"\item " + inline(content))
            i += 1
            # continuation lines of the same item
            while i < len(lines) and lines[i].strip() and not re.match(
                r"^(\s*)([-*+]|\d+[.)])\s+|^\s*#|^\s*```|^\s*>", lines[i]
            ) and len(lines[i]) - len(lines[i].lstrip()) > len(indent):
                out.append(inline(lines[i].strip()))
                i += 1
            continue

        close_lists()
        out.append(inline(stripped))
        i += 1

    close_lists()
    return "\n".join(out), meta


PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage{fontspec}
\usepackage[margin=2.4cm]{geometry}
\usepackage{longtable,booktabs,array}
\usepackage[hidelinks]{hyperref}
\usepackage{parskip}
\usepackage{amssymb}
\usepackage{fancyhdr}
\setmainfont{Helvetica Neue}[Scale=0.96]
\setmonofont{Menlo}[Scale=0.82]
\renewcommand{\arraystretch}{1.25}
\setlength{\LTpre}{6pt}\setlength{\LTpost}{10pt}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\footnotesize\textsc{%(runhead)s}}
\fancyhead[R]{\footnotesize\thepage}
\renewcommand{\headrulewidth}{0.2pt}
\begin{document}
"""


def tex_document(title: str, subtitle: str, bodies: list[str], toc: bool) -> str:
    runhead = re.sub(r"[^A-Za-z0-9 ,.-]", "", title)[:60]
    parts = [PREAMBLE % {"runhead": runhead}]
    parts.append(
        r"\begin{center}{\LARGE\bfseries " + latex_escape(title) + r"}\\[4pt]" + "\n"
        + (r"{\small " + latex_escape(subtitle) + r"}" if subtitle else "")
        + r"\end{center}" + "\n" + r"\vspace{4pt}\hrule\vspace{10pt}"
    )
    if toc:
        parts.append(r"{\small\tableofcontents}" + "\n" + r"\clearpage")
    parts.extend(bodies)
    parts.append(r"\end{document}")
    return "\n".join(parts)


def compile_pdf(tex: str, out_pdf: Path, quiet: bool) -> bool:
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="reviewpdf-") as tmp:
        job = Path(tmp) / "review"
        job.with_suffix(".tex").write_text(tex, encoding="utf-8")
        # Two passes: longtable column widths and the table of contents both
        # settle on the second.
        for _ in range(2):
            proc = subprocess.run(
                ["xelatex", "-interaction=nonstopmode", "-halt-on-error",
                 "review.tex"],
                cwd=tmp, capture_output=True, text=True,
            )
        produced = job.with_suffix(".pdf")
        if not produced.exists():
            if not quiet:
                log = proc.stdout + proc.stderr
                tail = [l for l in log.splitlines() if l.startswith("!")][:6]
                print(f"FAIL: xelatex produced no PDF for {out_pdf.name}",
                      file=sys.stderr)
                for l in tail:
                    print("      " + l, file=sys.stderr)
            return False
        shutil.copy(produced, out_pdf)
        return True


def meta_only(md: str) -> dict:
    meta, _ = parse_front_matter(md.replace("\r\n", "\n").split("\n"))
    return meta


def title_of(path: Path, md: str, meta: dict) -> str:
    if meta.get("title"):
        return meta["title"].strip('"')
    for line in md.split("\n"):
        m = re.match(r"^#\s+(.*)$", line.strip())
        if m:
            return m.group(1)
    return path.stem.replace("_", " ").replace("-", " ")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="+", help="Markdown source files")
    ap.add_argument("--packet", help="bind every file into one PDF at this path")
    ap.add_argument("--outdir", help="where per-file PDFs land (default: beside the source)")
    ap.add_argument("--title", help="packet title; default is the first file's title")
    ap.add_argument("--subtitle", default="", help="line under the title (e.g. the gate and date)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    sources = [Path(f) for f in args.files]
    missing = [p for p in sources if not p.is_file()]
    if missing:
        for p in missing:
            print(f"FAIL: {p} not found", file=sys.stderr)
        return 1

    if not shutil.which("xelatex"):
        print("FAIL: xelatex not on PATH; cannot render review PDFs", file=sys.stderr)
        return 1

    written: list[Path] = []

    if args.packet:
        bodies = []
        first_title = None
        for idx, path in enumerate(sources):
            md = path.read_text(encoding="utf-8", errors="replace")
            t = title_of(path, md, meta_only(md))
            body, _meta = convert(md, base_level=1, drop_title=t)
            first_title = first_title or t
            bodies.append(
                (r"\clearpage" if idx else "")
                + f"\n\\section*{{{latex_escape(t)}}}\n"
                + f"\\addcontentsline{{toc}}{{section}}{{{latex_escape(t)}}}\n"
                + r"{\footnotesize\texttt{" + latex_escape(str(path)) + r"}}\par\medskip" + "\n"
                + body
            )
        tex = tex_document(args.title or first_title or "Review packet",
                           args.subtitle, bodies, toc=len(sources) > 1)
        out = Path(args.packet)
        if not compile_pdf(tex, out, args.quiet):
            return 1
        written.append(out)
    else:
        for path in sources:
            md = path.read_text(encoding="utf-8", errors="replace")
            t = args.title or title_of(path, md, meta_only(md))
            body, _meta = convert(md, base_level=0, drop_title=t)
            tex = tex_document(t, args.subtitle or str(path), [body], toc=False)
            outdir = Path(args.outdir) if args.outdir else path.parent
            out = outdir / (path.stem + ".pdf")
            if not compile_pdf(tex, out, args.quiet):
                return 1
            written.append(out)

    for p in written:
        print(f"PDF: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
