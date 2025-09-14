# river_weather
Exploring sources UK river level and weather data for analysis

## River level data sources
Fairly straightforward, using the Environment Agency's [Hydrology Data Explorer](https://environment.data.gov.uk/hydrology/explore#/landing) and it's [API](https://environment.data.gov.uk/hydrology/doc/reference#stations-examples).  Each monitoring station has a unique id and a page, e.g. Todmorden Callis Bridge unique id is 0b5fd566-d9d1-4c66-8855-a096610cd1d1 and page is https://environment.data.gov.uk/hydrology/station/0b5fd566-d9d1-4c66-8855-a096610cd1d1.  15min Level (m) time series is available for download in CSV.  The API allows programmatic interaction.  Here's a table of monitoring stations:

| Station Name | Unique ID |
|---|---|
|[Todmorden Callis Bridge](https://environment.data.gov.uk/hydrology/station/0b5fd566-d9d1-4c66-8855-a096610cd1d1) |0b5fd566-d9d1-4c66-8855-a096610cd1d1|
|[Nutclough](https://environment.data.gov.uk/hydrology/station/35e2af93-dfc1-4a38-8cb1-26e3076c3941)|35e2af93-dfc1-4a38-8cb1-26e3076c3941|
|[Hebden Bridge](https://environment.data.gov.uk/hydrology/station/cc307b4d-a053-4282-9042-7b8a64fccd0e)|cc307b4d-a053-4282-9042-7b8a64fccd0e|
|[Mytholmroyd Dauber Bridge](https://environment.data.gov.uk/hydrology/station/9129bb7b-b639-4dac-83c4-2c6d3265ac21) |9129bb7b-b639-4dac-83c4-2c6d3265ac21 |
|[Mytholmroyd](https://environment.data.gov.uk/hydrology/station/8a2ef48d-ddc5-4643-a1cf-2da54a045d8e_F1204)|8a2ef48d-ddc5-4643-a1cf-2da54a045d8e_F1204|
|[Mytholmroyd (old)](https://environment.data.gov.uk/hydrology/station/8a2ef48d-ddc5-4643-a1cf-2da54a045d8e_L1204A)|8a2ef48d-ddc5-4643-a1cf-2da54a045d8e_L1204A|

## Weather data sources

There are two primary sources: Environment Agency rainfall gauges and personal weather stations hosted on [Weather Underground](https://www.wunderground.com/).  

### Environment Agency rainfall gauges
These can be accessed via the Environment Agency's [Hydrology Data Explorer](https://environment.data.gov.uk/hydrology/explore#/landing) and it's [API](https://environment.data.gov.uk/hydrology/doc/reference#stations-examples). The API is the same as above.  Some examples are:

| Station Name | Unique ID |
|---|---|
|[Gorpley](https://environment.data.gov.uk/hydrology/station/cbd85eb5-b6fe-4478-b2e8-245205ef84e3)|cbd85eb5-b6fe-4478-b2e8-245205ef84e3|
|[Bacup](https://environment.data.gov.uk/hydrology/station/3e0e16e2-862e-403a-8097-24648a6e3a3b)|3e0e16e2-862e-403a-8097-24648a6e3a3b|
|[Gorple](https://environment.data.gov.uk/hydrology/station/b71f87b9-99fc-4d54-bc8e-f1820ac74c94)|b71f87b9-99fc-4d54-bc8e-f1820ac74c94|
|[Walshaw Dean Lodge](https://environment.data.gov.uk/hydrology/station/445f2262-65b1-4904-9587-c9bdfea18d50)|445f2262-65b1-4904-9587-c9bdfea18d50|


### Weather Underground Personal Weather Stations
some links and stuff to explain wu

#### Weather Underground PWS Scraper

`scrape_wu.py` is a Python script designed to scrape fine-grained weather data from Weather Underground personal weather station (PWS) pages for a specific date or a range of dates.

#### Features

- Scrapes 5 minute weather data from Weather Underground's dashboard table.
- Supports scraping for a single date or a range of dates.
- Converts temperature values from Fahrenheit to Celsius.
- Parses and sorts time values correctly with full date context.
- Merges new data with existing CSV files, avoiding duplicates.
- Saves output to `data/weather/wu/{PWS_ID}.csv`.
- Provides verbose logging for debugging and progress tracking.


## Requirements

- Python 3.7+
- Playwright
- Pandas

Install dependencies using pip:
