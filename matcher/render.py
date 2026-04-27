"""Render Top-N recommendations to CSV / Markdown / HTML.

Each format goes into its own file under outputs/recommendations/<timestamp>/.
We never overwrite previous runs (CLAUDE.md: append-only result storage).

The renderer is dumb on purpose: it takes an already-sorted DataFrame and
the per-row score components and produces files. All ranking logic lives
in `matcher/score.py`.
"""
from __future__ import annotations

import csv
import html as htmllib
from pathlib import Path
from typing import Iterable

import pandas as pd


def _short(s: str, n: int = 240) -> str:
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= n else s[:n - 1] + "…"


def write_csv(top: pd.DataFrame, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cols = ["rank", "final", "base", "is_big_tech",
            "semantic", "keyword", "title_score",
            "platform", "title", "company", "city",
            "job_type", "seniority", "salary_raw", "url", "jd_excerpt"]
    cols = [c for c in cols if c in top.columns]
    top[cols].to_csv(out_path, index=False, encoding="utf-8-sig",
                     quoting=csv.QUOTE_MINIMAL)


def write_markdown(top: pd.DataFrame, out_path: Path,
                   meta_info: dict) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append(f"# ResuMiner Recommendations")
    lines.append("")
    lines.append(f"- generated: `{meta_info.get('timestamp', '')}`")
    lines.append(f"- resume: `{meta_info.get('resume_path', '')}`")
    lines.append(f"- candidates after filter: **{meta_info.get('after_filter', 0)}** "
                 f"of {meta_info.get('total', 0)}")
    lines.append(f"- model: `{meta_info.get('model', '')}`")
    weights = meta_info.get("weights", {})
    if weights:
        lines.append("- weights: " + ", ".join(f"{k}={v:.2f}" for k, v in weights.items()))
    btp = meta_info.get("big_tech_penalty", 1.0)
    if btp < 1.0:
        lines.append(
            f"- big-tech soft-deprioritization: ×{btp:.2f}  "
            f"({meta_info.get('big_tech_count_in_top', 0)} big-tech rows in Top-N)"
        )
    lines.append("")
    lines.append("## Filter stats")
    lines.append("")
    for k, v in (meta_info.get("filter_stats") or {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Top picks")
    lines.append("")

    big_tech_penalty = meta_info.get("big_tech_penalty", 1.0)

    for _, r in top.iterrows():
        big_tech_tag = ""
        if bool(r.get("is_big_tech", False)) and big_tech_penalty < 1.0:
            big_tech_tag = f"  *[大厂·已软降 ×{big_tech_penalty:.2f}]*"
        lines.append(
            f"### #{int(r['rank'])} · {r.get('title', '')}  ·  "
            f"{r.get('company', '')}{big_tech_tag}"
        )
        lines.append("")
        score_line = (
            f"- **score**: {r['final']:.3f}"
        )
        if "base" in r and bool(r.get("is_big_tech", False)) and big_tech_penalty < 1.0:
            score_line += f" (base {r['base']:.3f} × penalty {big_tech_penalty:.2f})"
        score_line += (
            f"  (semantic {r['semantic']:.2f} · keyword {r['keyword']:.2f} · "
            f"title {r['title_score']:.2f} · loc {r['location_score']:.2f} · "
            f"type {r['job_type_score']:.2f})"
        )
        lines.append(score_line)
        lines.append(
            f"- platform: `{r.get('platform','')}` · city: {r.get('city','')} · "
            f"type: {r.get('job_type','')} · seniority: {r.get('seniority','')}"
        )
        if r.get("salary_raw"):
            lines.append(f"- salary: {r['salary_raw']}")
        if r.get("url"):
            lines.append(f"- url: <{r['url']}>")
        lines.append("")
        lines.append(f"> {_short(r.get('jd_excerpt', ''), 400)}")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


_HTML_HEAD = """<!doctype html>
<html lang="zh-CN"><meta charset="utf-8">
<title>ResuMiner Recommendations</title>
<style>
  body { font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
         max-width: 980px; margin: 32px auto; padding: 0 16px; color: #1a1a1a; }
  h1 { margin-bottom: 4px; }
  .meta { color: #666; font-size: 13px; margin-bottom: 24px; }
  .card { border: 1px solid #e2e2e2; border-radius: 10px; padding: 16px;
          margin: 14px 0; background: #fff; }
  .card h3 { margin: 0 0 6px 0; }
  .card .row { color: #555; font-size: 13px; margin: 4px 0; }
  .score { display: inline-block; background: #0a7; color: #fff;
           padding: 2px 8px; border-radius: 6px; font-weight: 600; }
  .pill { display: inline-block; background: #f1f3f5; color: #444;
          padding: 1px 8px; border-radius: 999px; font-size: 12px;
          margin-right: 6px; }
  .pill.big-tech { background: #fff1e5; color: #b25800;
                   border: 1px solid #ffd6ad; }
  .jd { color: #333; font-size: 13.5px; line-height: 1.55;
        background: #fafafa; padding: 10px 12px; border-radius: 6px;
        white-space: pre-wrap; }
  a { color: #06c; text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>
"""


def write_html(top: pd.DataFrame, out_path: Path, meta_info: dict) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    parts: list[str] = [_HTML_HEAD]
    parts.append("<h1>ResuMiner Recommendations</h1>")

    weights = meta_info.get("weights", {})
    parts.append("<div class='meta'>")
    parts.append(f"generated: {htmllib.escape(meta_info.get('timestamp', ''))} · ")
    parts.append(f"resume: <code>{htmllib.escape(meta_info.get('resume_path', ''))}</code> · ")
    parts.append(f"candidates: {meta_info.get('after_filter', 0)} / {meta_info.get('total', 0)} · ")
    parts.append(f"model: <code>{htmllib.escape(meta_info.get('model', ''))}</code>")
    if weights:
        parts.append("<br>weights: " + ", ".join(
            f"{htmllib.escape(k)}={v:.2f}" for k, v in weights.items()))
    parts.append("</div>")

    big_tech_penalty = meta_info.get("big_tech_penalty", 1.0)

    for _, r in top.iterrows():
        url = htmllib.escape(str(r.get("url", "")))
        title = htmllib.escape(str(r.get("title", "")))
        company = htmllib.escape(str(r.get("company", "")))
        parts.append("<div class='card'>")
        title_html = (f"<a href='{url}' target='_blank'>{title}</a>"
                      if url else title)
        parts.append(
            f"<h3>#{int(r['rank'])} · {title_html}"
            f" <span class='score'>{r['final']:.3f}</span></h3>"
        )
        big_tech_pill = ""
        if bool(r.get("is_big_tech", False)) and big_tech_penalty < 1.0:
            big_tech_pill = (
                f"<span class='pill big-tech' title='final = base × {big_tech_penalty:.2f}'>"
                f"大厂·已软降 ×{big_tech_penalty:.2f}</span>"
            )
        parts.append(
            f"<div class='row'><b>{company}</b> · "
            f"{big_tech_pill}"
            f"<span class='pill'>{htmllib.escape(str(r.get('city','')))}</span>"
            f"<span class='pill'>{htmllib.escape(str(r.get('job_type','')))}</span>"
            f"<span class='pill'>{htmllib.escape(str(r.get('seniority','')))}</span>"
            f"<span class='pill'>{htmllib.escape(str(r.get('platform','')))}</span>"
            f"</div>"
        )
        score_detail = (
            f"semantic {r['semantic']:.2f} · keyword {r['keyword']:.2f} · "
            f"title {r['title_score']:.2f} · loc {r['location_score']:.2f} · "
            f"type {r['job_type_score']:.2f}"
        )
        if "base" in r and bool(r.get("is_big_tech", False)) and big_tech_penalty < 1.0:
            score_detail = f"base {r['base']:.3f} × {big_tech_penalty:.2f} · " + score_detail
        parts.append(f"<div class='row'>{score_detail}")
        if r.get("salary_raw"):
            parts.append(f" · salary {htmllib.escape(str(r['salary_raw']))}")
        parts.append("</div>")
        excerpt = htmllib.escape(_short(r.get("jd_excerpt", ""), 600))
        parts.append(f"<div class='jd'>{excerpt}</div>")
        parts.append("</div>")

    parts.append("</html>")
    out_path.write_text("".join(parts), encoding="utf-8")


def render_all(top: pd.DataFrame, out_dir: Path, meta_info: dict,
               formats: Iterable[str]) -> list[Path]:
    """Run all requested renderers; return list of written paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for fmt in formats:
        f = fmt.strip().lower()
        if f == "csv":
            p = out_dir / "recommendations.csv"
            write_csv(top, p)
        elif f in ("md", "markdown"):
            p = out_dir / "recommendations.md"
            write_markdown(top, p, meta_info)
        elif f == "html":
            p = out_dir / "recommendations.html"
            write_html(top, p, meta_info)
        else:
            continue
        paths.append(p)
    return paths
