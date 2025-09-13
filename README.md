# river_weather
Exploring sources UK river level and weather data for analysis

## River level data sources
Fairly straightforward, using the Environment Agency's [Hydrology Data Explorer](https://environment.data.gov.uk/hydrology/explore#/landing) and it's [API](https://environment.data.gov.uk/hydrology/doc/reference#stations-examples).  Examples

Monitoring station at Todmorden Callis Bridge has a unique id (0b5fd566-d9d1-4c66-8855-a096610cd1d1) and a page: https://environment.data.gov.uk/hydrology/station/0b5fd566-d9d1-4c66-8855-a096610cd1d1.  15min Level (m) time series is available for download in CSV.  The API allows programmatic interaction.  Here's a table of monitoring stations:

| Station Name | Unique ID |
|---|---|
|[Todmorden Callis Bridge](https://environment.data.gov.uk/hydrology/station/0b5fd566-d9d1-4c66-8855-a096610cd1d1) |0b5fd566-d9d1-4c66-8855-a096610cd1d1|
|[Nutclough](https://environment.data.gov.uk/hydrology/station/35e2af93-dfc1-4a38-8cb1-26e3076c3941)|35e2af93-dfc1-4a38-8cb1-26e3076c3941|
|[Hebden Bridge](https://environment.data.gov.uk/hydrology/station/cc307b4d-a053-4282-9042-7b8a64fccd0e)|cc307b4d-a053-4282-9042-7b8a64fccd0e|
|[Mytholmroyd Dauber Bridge](https://environment.data.gov.uk/hydrology/station/9129bb7b-b639-4dac-83c4-2c6d3265ac21) |9129bb7b-b639-4dac-83c4-2c6d3265ac21 |
|[Mytholmroyd](https://environment.data.gov.uk/hydrology/station/8a2ef48d-ddc5-4643-a1cf-2da54a045d8e_F1204)|8a2ef48d-ddc5-4643-a1cf-2da54a045d8e_F1204|
|[Mytholmroyd (old)](https://environment.data.gov.uk/hydrology/station/8a2ef48d-ddc5-4643-a1cf-2da54a045d8e_L1204A)|8a2ef48d-ddc5-4643-a1cf-2da54a045d8e_L1204A|


