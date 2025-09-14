import asyncio
import argparse
import os
import pandas as pd
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

# Function to fetch weather data for a specific date
async def fetch_weather_table(pws_id, date):
    url = f"https://www.wunderground.com/dashboard/pws/{pws_id}/table/{date}/{date}/daily"
    print(f"[INFO] Target URL: {url}")

    async with async_playwright() as p:
        print("[INFO] Launching browser...")
        browser = await p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
        # print("[SUCCESS] Browser launched.")
        page = await browser.new_page()
        print("[INFO] Navigating to page...")
        await page.goto(url, timeout=60000)
        print("[SUCCESS] Page loaded.  [INFO] Waiting for desktop table rows to appear...")

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

        print("[INFO] Extracting table rows using innerText with fallback ...")
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

# Function to scrape and store weather data for a specific date
async def scrape_and_store(pws_id, date):
    print(f"[INFO] Starting scrape for PWS ID: {pws_id} on {date}")
    new_data = await fetch_weather_table(pws_id, date)
    if new_data.empty:
        raise ValueError("No valid data rows found in the table.")
    if "Time" not in new_data.columns:
        raise ValueError("Missing 'Time' column in scraped data.")

    print("[INFO] Parsing and sorting time column...")
    new_data["Time"] = pd.to_datetime(date + " " + new_data["Time"], format="%Y-%m-%d %I:%M %p", errors="coerce")
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
            existing_df["Time"] = pd.to_datetime(existing_df["Time"], errors="coerce")
        combined_df = pd.concat([existing_df, new_data]).drop_duplicates(subset=["Time"]).sort_values("Time")
    else:
        print("[INFO] No existing file. Creating new one.")
        metadata = [f"# PWS_ID: {pws_id}\n"]
        combined_df = new_data

    print(f"[INFO] Writing data to {file_path}")
    with open(file_path, "w") as f:
        f.writelines(metadata)
        combined_df.to_csv(f, index=False)
    print(f"[INFO] -------- Done! --------")

# Main execution block
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Weather Underground PWS data.")
    parser.add_argument("pws_id", type=str, help="Personal Weather Station ID")
    parser.add_argument("--start_date", type=str, help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end_date", type=str, help="End date in YYYY-MM-DD format")
    args = parser.parse_args()

    if args.start_date and args.end_date:
        start = datetime.strptime(args.start_date, "%Y-%m-%d")
        end = datetime.strptime(args.end_date, "%Y-%m-%d")
        if end < start:
            raise ValueError("--start_date must be earlier than --end_date")
        elif start < end:
            current = start
            while current <= end:
                asyncio.run(scrape_and_store(args.pws_id, current.strftime("%Y-%m-%d")))
                current += timedelta(days=1)
        elif start == end:
            raise ValueError("single date scraping not implemented.  Provide a bracket of at least 2 days.")
    else:
        raise ValueError("Both --start_date and --end_date must be provided.")

