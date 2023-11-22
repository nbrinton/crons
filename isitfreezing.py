import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

import mailtrap as mt
import os
import requests

# Open Meteo variables
om_base_url = 'https://api.open-meteo.com'
om_version = 'v1'


def send_email(freezing_days):
    message = 'There are some chilly days headed your way!\n'

    for day in freezing_days:
        message += f'{day[0]}: {day[1]}\n'

    # create mail object
    mail = mt.Mail(
        sender=mt.Address(email='mycrons@nbrinton.dev', name='MyCrons at nbrintondev'),
        to=[mt.Address(email='nathanbrinton@outlook.com')],
        subject='Freeze Alert',
        text=message,
    )

    # create client and send
    client = mt.MailtrapClient(token=os.environ['MAILTRAP_SMTP_PASSWORD'])
    client.send(mail)

def my_way():
    payload = {
        'forecast_days': 16,
        'latitude': 43.582030,
        'longitude': -116.198210,
        'timezone': 'MST',
        'daily': ['temperature_2m_min', 'apparent_temperature_min'],
        'temperature_unit': 'fahrenheit'
    }

    res = requests.get(f'{om_base_url}/{om_version}/forecast', params=payload)
    res_json = res.json()

    days = res_json['daily']['time']
    temp_2m_mins = res_json['daily']['temperature_2m_min']
    temp_apparent_mins = res_json['daily']['apparent_temperature_min']

    # Combine the disparate arrays into one array of tuples
    data = zip(days, temp_2m_mins, temp_apparent_mins)

    freezing_days = []

    for d in data:
        day = d[0]
        temp_2m_min = d[1]
        temp_apparent_min = d[2]

        print(str(d) + ' YEAP' if temp_2m_min <= 32.0 else str(d) + ' NOPE')
        if float(temp_2m_min) <= 32.0:
            print(f'{str(d)} YEAP: {temp_2m_min}')
            freezing_days.append(d)
        else:
            print(f'{str(d)} NOPE: {temp_2m_min}')

    if len(freezing_days) > 0:
        send_email(freezing_days=freezing_days)


def meteo_way():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 43.58203,
        "longitude": -116.19821,
        "daily": ["temperature_2m_min", "apparent_temperature_min"],
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "America/Denver",
        "forecast_days": 16
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_min = daily.Variables(0).ValuesAsNumpy()
    daily_apparent_temperature_min = daily.Variables(1).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s"),
        end=pd.to_datetime(daily.TimeEnd(), unit="s"),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    )}
    daily_data["temperature_2m_min"] = daily_temperature_2m_min
    daily_data["apparent_temperature_min"] = daily_apparent_temperature_min

    daily_dataframe = pd.DataFrame(data=daily_data)
    print(daily_dataframe)


if __name__ == '__main__':
    # my_way()
    meteo_way()
