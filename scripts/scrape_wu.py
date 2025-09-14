import asyncio
import argparse
import os
import pandas as pd
import json
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

# Function to fetch weather data and metadata for a specific date
async def fetch_weather_table_and_metadata(pws_id, date):
    url = f"https://www.wunderground.com/dashboard/pws/{pws_id}/table/{date}/{date}/daily"
    print(f"[INFO] Target URL: {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
        page = await browser.new_page()
        await page.goto(url, timeout=60000)

        try:
            await page.wait_for_selector("table.history-table.desktop-table tbody tr", state="attached", timeout=30000)
        except Exception as e:
            print("[ERROR] Table rows not found:", e)
            await browser.close()
            return pd.DataFrame(), {}

        headers = await page.eval_on_selector_all(
            "table.history-table.desktop-table thead tr th",
            "els => els.map(e => e.innerText.trim())"
        )

        rows = await page.eval_on_selector_all(
            "table.history-table.desktop-table tbody tr",
            """els => els.map(row =>
                Array.from(row.querySelectorAll('td')).map(cell =>
                    cell.innerText.trim() || cell.textContent.trim()
                )
            )"""
        )

        valid_rows = [row for row in rows if len(row) == len(headers)]

        # Extract metadata from embedded JSON
        metadata_dict = {}
        try:
            metadata_json = await page.eval_on_selector("script#app-root-state", "el => el.textContent")
            parsed_json = json.loads(metadata_json)
            for section in parsed_json.values():
                if isinstance(section, dict) and "b" in section and "ID" in section["b"]:
                    b = section["b"]
                    metadata_dict = {
                        "#pwsName": b.get("name", ""),
                        "#lat": b.get("latitude", ""),
                        "#lon": b.get("longitude", ""),
                        "#elev": b.get("elevation", ""),
                        "#height": b.get("height", ""),
                        "#stationType": b.get("stationType", "")
                    }
                    break
        except Exception as e:
            print("[ERROR] Metadata extraction failed:", e)

        await browser.close()
        return pd.DataFrame(valid_rows, columns=headers), metadata_dict

# Function to scrape and store weather data
async def scrape_and_store(pws_id, date):
    print(f"[INFO] Scraping PWS ID: {pws_id} on {date}")
    new_data, new_metadata = await fetch_weather_table_and_metadata(pws_id, date)

    if new_data.empty:
        raise ValueError("No valid data rows found.")
    if "Time" not in new_data.columns:
        raise ValueError("Missing 'Time' column.")

    new_data["Time"] = pd.to_datetime(date + " " + new_data["Time"], format="%Y-%m-%d %I:%M %p", errors="coerce")
    new_data = new_data.dropna(subset=["Time"]).sort_values("Time")

    os.makedirs("data/weather/wu", exist_ok=True)
    file_path = f"data/weather/wu/{pws_id}.csv"

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            lines = f.readlines()

        metadata_lines = [line for line in lines if line.startswith("#")]
        data_lines = [line for line in lines if not line.startswith("#")]

        # Parse existing metadata
        existing_metadata = {}
        for line in metadata_lines:
            if ":" in line:
                key, value = line.strip().split(":", 1)
                existing_metadata[key.strip()] = value.strip()

        # Merge metadata
        for key, value in new_metadata.items():
            if key not in existing_metadata or existing_metadata[key] != str(value):
                existing_metadata[key] = str(value)

        # Reconstruct metadata lines
        metadata_lines = [f"{key}: {value}\n" for key, value in existing_metadata.items()]

        from io import StringIO
        existing_df = pd.read_csv(StringIO("".join(data_lines)))
        if "Time" in existing_df.columns:
            existing_df["Time"] = pd.to_datetime(existing_df["Time"], errors="coerce")
        combined_df = pd.concat([existing_df, new_data]).drop_duplicates(subset=["Time"]).sort_values("Time")

    else:
        metadata_lines = [f"# PWS_ID: {pws_id}\n"]
        for key, value in new_metadata.items():
            metadata_lines.append(f"{key}: {value}\n")
        combined_df = new_data

    with open(file_path, "w") as f:
        f.writelines(metadata_lines)
        combined_df.to_csv(f, index=False)

    print(f"[INFO] Data written to {file_path}")

# Main execution
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
        current = start
        while current <= end:
            asyncio.run(scrape_and_store(args.pws_id, current.strftime("%Y-%m-%d")))
            current += timedelta(days=1)
    else:
        raise ValueError("Both --start_date and --end_date must be provided.")
