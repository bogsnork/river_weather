
import asyncio
import argparse
import os
import pandas as pd
from playwright.async_api import async_playwright

async def fetch_weather_table(pws_id, date):
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
        print("[INFO] Waiting for desktop table rows to appear...")

        try:
            await page.wait_for_selector("table.history-table.desktop-table tbody tr", state="attached", timeout=30000)
            print("[SUCCESS] Desktop table rows detected.")
        except Exception as e:
            print("[ERROR] Desktop table rows not found:", e)
            await browser.close()
            return pd.DataFrame()

        print("[INFO] Extracting table headers...")
        headers = await page.eval_on_selector_all(
            "table.history-table.desktop-table thead tr th",
            "els => els.map(e => e.innerText.trim())"
        )
        print("[SUCCESS] Headers found:", headers)

        print("[INFO] Extracting table rows using Strategy 5 (innerText with fallback)...")
        rows = await page.eval_on_selector_all(
            "table.history-table.desktop-table tbody tr",
            """els => els.map(row =>
                Array.from(row.querySelectorAll('td')).map(cell =>
                    cell.innerText.trim() || cell.textContent.trim()
                )
            )"""
        )

        valid_rows = [row for row in rows if len(row) == len(headers)]
        print(f"[SUCCESS] Extracted {len(valid_rows)} valid rows matching header length.")
        if valid_rows:
            print("[INFO] First 3 rows of data:")
            for row in valid_rows[:3]:
                print(row)
        else:
            print("[WARNING] No valid rows matched header length.")

        await browser.close()
        return pd.DataFrame(valid_rows, columns=headers)

async def scrape_and_store(pws_id, date):
    print(f"[INFO] Starting scrape for PWS ID: {pws_id} on {date}")
    new_data = await fetch_weather_table(pws_id, date)
    if new_data.empty:
        raise ValueError("No valid data rows found in the table.")
    if "Time" not in new_data.columns:
        raise ValueError("Missing 'Time' column in scraped data.")

    print("[INFO] Parsing and sorting time column...")
    new_data["Time"] = pd.to_datetime(new_data["Time"], format="%I:%M %p", errors="coerce")
    new_data = new_data.dropna(subset=["Time"])
    new_data = new_data.sort_values("Time")

    os.makedirs("data/weather/wu", exist_ok=True)
    file_path = f"data/weather/wu/{pws_id}.csv"

    if os.path.exists(file_path):
        print("[INFO] Existing file found. Merging with new data...")
        with open(file_path, "r") as f:
            lines = f.readlines()
        metadata = [line for line in lines if line.startswith("#")]
        data_lines = [line for line in lines if not line.startswith("#")]
        from io import StringIO
        existing_df = pd.read_csv(StringIO("".join(data_lines)))
        if "Time" in existing_df.columns:
            existing_df["Time"] = pd.to_datetime(existing_df["Time"], format="%I:%M %p", errors="coerce")
        combined_df = pd.concat([existing_df, new_data]).drop_duplicates(subset=["Time"]).sort_values("Time")
    else:
        print("[INFO] No existing file. Creating new one.")
        metadata = [f"# PWS_ID: {pws_id}\n"]
        combined_df = new_data

    print(f"[INFO] Writing data to {file_path}")
    with open(file_path, "w") as f:
        f.writelines(metadata)
        combined_df.to_csv(f, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Weather Underground PWS data.")
    parser.add_argument("pws_id", type=str, help="Personal Weather Station ID")
    parser.add_argument("date", type=str, help="Date in YYYY-MM-DD format")
    args = parser.parse_args()
    asyncio.run(scrape_and_store(args.pws_id, args.date))
