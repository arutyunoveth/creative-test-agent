import os

PRINT_CSS = """
@media print {
  body { font-family: 'Times New Roman', Times, serif; font-size: 12pt; line-height: 1.5; color: #000; }
  h1 { font-size: 18pt; border-bottom: 2px solid #000; padding-bottom: 4pt; }
  h2 { font-size: 14pt; margin-top: 18pt; }
  table { width: 100%; border-collapse: collapse; margin: 12pt 0; }
  th, td { border: 1px solid #000; padding: 4pt 8pt; text-align: left; }
  th { background-color: #eee; }
  .page-break { page-break-before: always; }
  .risk-high { color: #c00; }
  .risk-medium { color: #c60; }
  .risk-low { color: #080; }
}
"""


def build_pdf_ready_html(markdown_content: str, html_content: str | None, title: str, output_path: str) -> str:
    body = html_content or _md_to_simple_html(markdown_content)
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{_escape(title)}</title>
<style>{PRINT_CSS}</style>
</head>
<body>
{body}
</body>
</html>"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    return output_path


def _escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _md_to_simple_html(md: str) -> str:
    lines = []
    for line in md.split("\n"):
        if line.startswith("# "):
            lines.append(f"<h1>{_escape(line[2:])}</h1>")
        elif line.startswith("## "):
            lines.append(f"<h2>{_escape(line[3:])}</h2>")
        elif line.startswith("### "):
            lines.append(f"<h3>{_escape(line[4:])}</h3>")
        elif line.startswith("| "):
            continue
        elif line.startswith("- **["):
            lines.append(f"<p>{_escape(line)}</p>")
        elif line.startswith("- "):
            lines.append(f"<li>{_escape(line[2:])}</li>")
        elif line.strip():
            lines.append(f"<p>{_escape(line)}</p>")
    return "\n".join(lines)
