
import asyncio
import pandas as pd
import os
from datetime import datetime
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import io

async def fetch_weather_table(pws_id, date):
    url = f"https://www.wunderground.com/dashboard/pws/{pws_id}/table/{date}/{date}/daily"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
        page = await browser.new_page()
        await page.goto(url, timeout=60000)

        try:
            await page.wait_for_selector("text='No data available'", state="detached", timeout=30000)
        except:
            print("Warning: 'No data available' message did not disappear. Proceeding anyway.")

        await page.wait_for_selector("table tbody tr", timeout=30000)

        content = await page.content()
        await browser.close()

    soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table")
    if not table:
        raise ValueError("No table found on the page.")

    headers = [th.text.strip() for th in table.find("thead").find_all("th")]
    rows = []
    for tr in table.find("tbody").find_all("tr"):
        cells = [td.text.strip() for td in tr.find_all("td")]
        if len(cells) == len(headers):
            rows.append(cells)

    if not rows:
        raise ValueError("No valid data rows found in the table.")

    df = pd.DataFrame(rows, columns=headers)
    df["Time"] = pd.to_datetime(df["Time"], format="%I:%M %p")
    df = df.sort_values("Time")
    return df

async def scrape_and_store(pws_id, date):
    new_data = await fetch_weather_table(pws_id, date)
    data_dir = os.path.join("data", "weather", "wu")
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, f"{pws_id}.csv")

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            lines = f.readlines()
        metadata = [line for line in lines if line.startswith("#")]
        data_lines = [line for line in lines if not line.startswith("#")]
        existing_df = pd.read_csv(io.StringIO("".join(data_lines)))
        existing_df["Time"] = pd.to_datetime(existing_df["Time"])
        combined_df = pd.concat([existing_df, new_data]).drop_duplicates(subset=["Time"]).sort_values("Time")
    else:
        metadata = [f"# PWS_ID: {pws_id}\n"]
        combined_df = new_data

    with open(file_path, "w") as f:
        f.writelines(metadata)
        combined_df.to_csv(f, index=False)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Scrape Weather Underground PWS data")
    parser.add_argument("pws_id", type=str, help="Personal Weather Station ID")
    parser.add_argument("date", type=str, help="Date in YYYY-MM-DD format")
    args = parser.parse_args()

    asyncio.run(scrape_and_store(args.pws_id, args.date))
