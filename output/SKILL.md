---
name: "cdp-crawler-optimizer"
description: "Uses CDP to bypass WAFs and auto-verifies scraped data completeness. Invoke when crawlers get blocked, return empty fields, or efficiency is low."
---

# CDP Crawler Optimizer

This skill ensures high-quality, anti-bot resilient web scraping by combining Chrome DevTools Protocol (CDP) and automated data validation. It guarantees that the crawler does not fail silently and that extracted fields are complete.

## 1. WAF Bypass via CDP
- **Trigger:** When facing severe WAF/anti-bot (e.g., Cloudflare, custom captchas on job platforms).
- **Action:** Connect to a manually authenticated Chrome instance using `--remote-debugging-port=9222`.
- **Implementation:** 
  - Use Playwright's `connect_over_cdp`. Do not rely solely on simple HTTP requests.
  - Intercept raw JSON data via `page.on("response")`.
  - Alternatively, use `page.evaluate` to execute `window.fetch` inside the browser context to natively inherit all real cookies and tokens.

## 2. Field Completeness & Auto-Optimization
- **Trigger:** When scraped data is missing expected fields (e.g., missing salary, missing job description) or pagination fails.
- **Action:** Implement a strict validation loop after each scraping action.
- **Implementation:**
  - Drive UI pagination via `page.mouse.wheel` or `locator.click`, mimicking human behavior to avoid detection.
  - Define a strict schema for the required data (e.g., Pydantic or TypedDict).
  - Check the extracted data against the schema immediately.
  - If fields are missing or empty, automatically adjust the parsing logic (e.g., fallback CSS selectors, wait times) or trigger a page reload/retry.

## 3. Output Verification
- **Post-run Checks:** Always output a summary of scraped items versus expected items.
- **Alerting:** If the success rate or field completeness drops below a configured threshold (e.g., 90%), log a clear error warning the user that the site structure might have changed or WAF rules have tightened.
