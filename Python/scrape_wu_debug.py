
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

async def debug_scrape_wu(pws_id, date):
    url = f"https://www.wunderground.com/dashboard/pws/{pws_id}/table/{date}/{date}/daily"
    print(f"[INFO] Target URL: {url}")

    try:
        print("[INFO] Launching browser...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
            print("[SUCCESS] Browser launched.")

            context = await browser.new_context()
            page = await context.new_page()

            print("[INFO] Navigating to page...")
            await page.goto(url, timeout=60000)
            print("[SUCCESS] Page loaded.")

            print("[INFO] Waiting for table rows to appear...")
            await page.wait_for_selector("table.history-table tbody tr", state="attached", timeout=30000)
            print("[SUCCESS] Table rows detected.")

            print("[INFO] Extracting table headers...")
            headers = await page.eval_on_selector_all(
                "table.history-table thead tr th",
                "elements => elements.map(el => el.innerText.trim())"
            )
            print(f"[SUCCESS] Headers found: {headers}")

            print("[INFO] Extracting table rows...")
            rows = await page.eval_on_selector_all(
                "table.history-table tbody tr",
                "rows => rows.map(row => Array.from(row.querySelectorAll('td')).map(cell => cell.innerText.trim()))"
            )

            if not rows:
                print("[ERROR] No data rows found.")
                return

            print(f"[SUCCESS] Extracted {len(rows)} rows.")
            print("[INFO] First 3 rows of data:")
            for row in rows[:3]:
                print(row)

            await browser.close()

    except PlaywrightTimeoutError as e:
        print(f"[TIMEOUT ERROR] {e}")
    except Exception as e:
        print(f"[UNEXPECTED ERROR] {e}")

# Entry point for script execution
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python scrape_wu_debug.py <PWS_ID> <YYYY-MM-DD>")
    else:
        asyncio.get_event_loop().run_until_complete(debug_scrape_wu(sys.argv[1], sys.argv[2]))
