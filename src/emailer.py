from __future__ import annotations

import html
import os
import smtplib
from email.message import EmailMessage

from src.config import EmailConfig
from src.models import Digest, Paper
from src.text_cleaning import clean_abstract, clean_text


def render_text_digest(digest: Digest) -> str:
    sections = ["Zotero Paper Digest", ""]
    if digest.new_papers:
        sections.append(render_text_section("New papers", digest.new_papers))
        sections.append("")
    if digest.classic_papers:
        sections.append(render_text_section("Classic papers", digest.classic_papers))
    return "\n".join(sections)


def render_text_section(title: str, papers: list[Paper]) -> str:
    lines = [title, "=" * len(title)]
    if not papers:
        return "\n".join(lines)
    for index, paper in enumerate(papers, 1):
        abstract = clean_abstract(paper.abstract)
        lines.extend(
            [
                f"{index}. {clean_text(paper.title)}",
                f"   Category: {paper.category}",
                f"   Year: {paper.year or 'Unknown'}",
                f"   Venue: {clean_text(paper.venue) or 'Unknown'}",
                f"   DOI: {clean_text(paper.doi) or 'N/A'}",
                f"   URL: {clean_text(paper.url) or 'N/A'}",
                f"   Abstract: {snippet(abstract, 700) or 'N/A'}",
                f"   Why: {clean_text(paper.why_recommended) or 'Relevant to the seed collection.'}",
                "",
            ]
        )
    return "\n".join(lines)


def render_html_digest(digest: Digest) -> str:
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: Georgia, 'Times New Roman', serif; color: #1f2933; line-height: 1.55; }}
    .paper {{ border-bottom: 1px solid #d9e2ec; padding: 14px 0; }}
    .meta {{ color: #52606d; font-size: 14px; }}
    .category {{ display: inline-block; padding: 2px 8px; border-radius: 999px; background: #e0f2fe; color: #075985; font-size: 12px; }}
  </style>
</head>
<body>
  <h1>Zotero Paper Digest</h1>
  {render_html_section("New papers", digest.new_papers) if digest.new_papers else ""}
  {render_html_section("Classic papers", digest.classic_papers) if digest.classic_papers else ""}
</body>
</html>"""


def render_html_section(title: str, papers: list[Paper]) -> str:
    if not papers:
        return ""
    items = []
    for paper in papers:
        title_html = html.escape(clean_text(paper.title))
        url = html.escape(clean_text(paper.url or ""))
        title_line = f'<a href="{url}">{title_html}</a>' if url else title_html
        abstract = clean_abstract(paper.abstract)
        items.append(
            f"""<article class="paper">
  <h3>{title_line}</h3>
  <p><span class="category">{html.escape(paper.category)}</span></p>
  <p class="meta">{html.escape(str(paper.year or "Unknown"))} - {html.escape(clean_text(paper.venue) or "Unknown venue")}</p>
  <p><strong>DOI:</strong> {html.escape(clean_text(paper.doi) or "N/A")}</p>
  <p><strong>URL:</strong> {f'<a href="{url}">{url}</a>' if url else "N/A"}</p>
  <p><strong>Abstract:</strong> {html.escape(snippet(abstract, 900) or "N/A")}</p>
  <p><strong>Why recommended:</strong> {html.escape(clean_text(paper.why_recommended) or "Relevant to the seed collection.")}</p>
</article>"""
        )
    return f"<h2>{html.escape(title)}</h2>{''.join(items)}"


def send_digest_email(config: EmailConfig, digest: Digest) -> None:
    message = EmailMessage()
    message["Subject"] = "Daily Zotero Paper Digest"
    message["From"] = config.from_email
    message["To"] = config.to_email
    text = render_text_digest(digest)
    html_body = render_html_digest(digest)
    message.set_content(text)
    message.add_alternative(html_body, subtype="html")

    smtp_user = os.environ["SMTP_USER"]
    smtp_pass = os.environ["SMTP_PASS"]
    if config.smtp_port == 465:
        with smtplib.SMTP_SSL(config.smtp_host, config.smtp_port, timeout=30) as smtp:
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(message)


def snippet(text: str, max_chars: int) -> str:
    compact = clean_text(text)
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3].rstrip() + "..."
