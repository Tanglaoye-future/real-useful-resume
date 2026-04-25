## Source

- Terminal session capture from Cursor integrated terminal
- Captured file: `/Users/franktang/.cursor/projects/Users-franktang-projects/terminals/4.txt`

## Metadata (from terminal header)

```text
pid: 6241
cwd: /Users/franktang/projects/resuminer
active_command: claude
last_command: cd resuminer
last_exit_code: 0
```

## Transcript excerpt (tail)

```text
⏺ Also remove the now-unused company_industry/company_stage/company_size fields from the card enrichment in format_data since we no longer
  get them from an API.

⏺ Update(core/crawler_engine/spiders/shixiseng_v2.py)
  ⎿  Removed 3 lines
      298                      employment_type="实习",
      299                      source_job_id=jd_url.split("/")[-1].split("?")[0],
      300                      source_keyword=self.keyword,
      301 -                    company_industry=card.get("company_industry", ""),
      302 -                    company_stage=card.get("company_stage", ""),
      303 -                    company_size=card.get("company_size", ""),
      301                  )
      302                  all_jobs.append(parsed)
      303

⏺ Verify syntax, add fonttools to requirements.txt, then run the test:

⏺ Bash(python3 -c "import ast
      with open('core/crawler_engine/spiders/shixiseng_v2.py') as f: ast.parse(f.read())…)
  ⎿  Syntax OK

  Searched for 1 pattern, read 1 file (ctrl+o to expand)

⏺ Update(requirements.txt)
  ⎿  Added 1 line
       8  sentence-transformers>=2.2.0
       9
      10  # 爬虫依赖
      11 +fonttools>=4.40.0
      12  requests>=2.31.0
      13  urllib3>=2.0.0
      14  certifi>=2023.7.22

⏺ Bash(.venv/bin/python test_shixiseng.py 2>&1)
  ⎿  2 extra bytes in post.stringData array
     2 extra bytes in post.stringData array
     2 extra bytes in post.stringData array
     … +42 lines (ctrl+o to expand)
  ⎿  (timeout 5m)

⏺ All green. Here's the final status:

  ---
  All issues resolved. Test passing 100%.

  ┌─────────────────┬────────────────────────────────────────┬──────────────────────┐
  │      Check      │                 Before                 │        After         │
  ├─────────────────┼────────────────────────────────────────┼──────────────────────┤
  │ JD content      │ 0/0 (always empty)                     │ 40/40                │
  ├─────────────────┼────────────────────────────────────────┼──────────────────────┤
  │ Salary          │ \ue866\ue042\ue042-\uf665... (garbled) │ 200-300/天 (decoded) │
  ├─────────────────┼────────────────────────────────────────┼──────────────────────┤
  │ job_description │ empty                                  │ populated            │
  ├─────────────────┼────────────────────────────────────────┼──────────────────────┤
  │ job_requirement │ empty                                  │ populated            │
  ├─────────────────┼────────────────────────────────────────┼──────────────────────┤
  │ URLs            │ ✓                                      │ ✓                    │
  ├─────────────────┼────────────────────────────────────────┼──────────────────────┤
  │ job_name        │ ✓                                      │ ✓                    │
  ├─────────────────┼────────────────────────────────────────┼──────────────────────┤
  │ company_name    │ ✓                                      │ ✓                    │
  └─────────────────┴────────────────────────────────────────┴──────────────────────┘

  Root causes found and fixed:

  1. JD detail fetch — spider wasn't visiting detail pages at all. Fixed with inline Playwright navigation and 12-selector cascade.
  2. Salary font obfuscation — Shixiseng uses a randomly-remapped custom WOFF font per page load where PUA characters (U+E042 etc.) display
  as digits. Fixed by intercepting the iconfonts/file response in-flight during page.goto(), parsing it with fonttools, and applying the
  decoded map to salary strings. The 2 extra bytes warning is a benign quirk in their font's post table.
  3. CDP wastage for Shixiseng — fetch_detail() was attempting CDP (which has no Shixiseng support) before falling through to RPC, adding
  unnecessary latency. Fixed with a domain != "shixiseng" guard.
  4. job_requirement always empty — parse_shixiseng_item hardcoded job_requirement: "". Fixed to pass through the split field from
  format_data.

✻ Brewed for 16m 36s

※ recap: Debugging and fixing the Shixiseng crawling pipeline to collect all Shanghai internship listings with JD content. All known bugs
  are now fixed and tests pass. Next: run a full crawl across all 8 keywords to validate at scale. (disable recaps in /config)
```

