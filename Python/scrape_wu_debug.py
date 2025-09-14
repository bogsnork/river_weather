import sys
import nest_asyncio
import asyncio
from playwright.async_api import async_playwright

nest_asyncio.apply()

async def debug_scrape(pws_id, date):
    url = f"https://www.wunderground.com/dashboard/pws/{pws_id}/table/{date}/{date}/daily"
    print(f"[INFO] Target URL: {url}")

    async with async_playwright() as p:
        print("[INFO] Launching browser...")
        browser = await p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
        print("[SUCCESS] Browser launched.")
        page = await browser.new_page()
        print("[INFO] Navigating to page...")
        await page.goto(url, timeout=60000)
        print("[SUCCESS] Page loaded.")
        print("[INFO] Waiting for desktop table to appear...")

        try:
            await page.wait_for_selector("table.history-table.desktop-table tbody tr", state="attached", timeout=30000)
            print("[SUCCESS] Desktop table rows detected.")
        except Exception as e:
            print(f"[ERROR] Desktop table rows not found: {e}")
            await browser.close()
            return

        print("[INFO] Extracting table headers...")
        headers = await page.eval_on_selector_all(
            "table.history-table.desktop-table thead tr th",
            "els => els.map(e => e.innerText.trim())"
        )
        print(f"[SUCCESS] Headers found ({len(headers)}): {headers}")

        strategies = [
            ("Strategy 1: td only", "els => els.map(row => Array.from(row.querySelectorAll('td')).map(cell => cell.innerText.trim()))"),
            ("Strategy 2: td strong only", "els => els.map(row => Array.from(row.querySelectorAll('td strong')).map(cell => cell.innerText.trim()))"),
            ("Strategy 3: td and strong", "els => els.map(row => Array.from(row.querySelectorAll('td, td strong')).map(cell => cell.textContent.trim()))"),
            ("Strategy 4: all textContent from td", "els => els.map(row => Array.from(row.querySelectorAll('td')).map(cell => cell.textContent.trim()))"),
            ("Strategy 5: td innerText and fallback to textContent", "els => els.map(row => Array.from(row.querySelectorAll('td')).map(cell => cell.innerText.trim() || cell.textContent.trim()))")
        ]

        for name, js in strategies:
            print(f"\n[INFO] Trying {name}...")
            try:
                rows = await page.eval_on_selector_all("table.history-table.desktop-table tbody tr", js)
                valid_rows = [r for r in rows if len(r) == len(headers)]
                print(f"[INFO] Extracted {len(rows)} rows, {len(valid_rows)} valid rows matching header length.")
                if valid_rows:
                    print("[SUCCESS] Valid rows found. First 3 rows:")
                    for row in valid_rows[:3]:
                        print(row)
                else:
                    print("[WARNING] No valid rows matched header length.")
            except Exception as e:
                print(f"[ERROR] Failed to extract rows using {name}: {e}")

        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scrape_wu_debug.py <PWS_ID> <YYYY-MM-DD>")
    else:
        asyncio.get_event_loop().run_until_complete(debug_scrape(sys.argv[1], sys.argv[2]))
