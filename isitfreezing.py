import mailtrap as mt
import openmeteo_requests as omr
import os
import pandas as pd
import requests
import requests_cache
from retry_requests import retry


def my_simple_email(freezing_days):
    # My first stab at sending a simple email using the list of freezing_days from my_simple_way()

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


def my_simple_way():
    # My first stab at requesting Open Meteo data and doing some ETL on it

    # Open Meteo variables
    om_base_url = 'https://api.open-meteo.com'
    om_version = 'v1'

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
        my_simple_email(freezing_days=freezing_days)


def meteo_way():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = omr.Client(session=retry_session)

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

    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s"),
            end=pd.to_datetime(daily.TimeEnd(), unit="s"),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"),
        "temperature_2m_min": daily_temperature_2m_min,
        "apparent_temperature_min": daily_apparent_temperature_min
    }

    daily_dataframe = pd.DataFrame(data=daily_data)

    return daily_dataframe


def send_email(table):
    html = """
        <!doctype html>
        <html>
          <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
          </head>
          <body style="font-family: sans-serif;">
            <div style="display: block; margin: auto; max-width: 600px;" class="main">
              <h1 style="font-size: 18px; font-weight: bold; margin-top: 20px">
                Incoming freezing temps!
              </h1>
              <p>There's some chilly weather headed your way! Make sure to keep that heater on and have come cocoa nearby!</p>
              """

    html += table

    html += """
                </div>
                <!-- Example of invalid for email html/css, will be detected by Mailtrap: -->
                <style>
                  .main { background-color: white; }
                  a:hover { border-left-width: 1em; min-height: 2em; }
                  
                  tr:nth-child(even) { background-color: #D6EEEE; }
                  th, td { width: 100px; max-width: 100px; }
                  th { text-align: left; }
                </style>
              </body>
            </html>
            """

    mail = mt.Mail(
        sender=mt.Address(email="mycrons@nbrinton.dev", name="MyCrons at nbrinton.dev"),
        to=[mt.Address(email="nathanbrinton@outlook.com", name="Nathan Brinton")],
        subject="Freeze Alert",
        html=html,
    )

    client = mt.MailtrapClient(token=os.environ['MAILTRAP_KEY'])
    client.send(mail)


def gen_html_table(pdf):
    # Generate an html table from the given pandas dataframe object

    html = """
        <table>
            <tr>
                <th style='width: 20px'></th>
                <th>Day</th>
                <th>Date</th>
                <th>Apparent Min Temp</th>
                <th>Min Temp 2 Meters above ground</th>
            </tr>
        """

    # Source: https://stackoverflow.com/a/16476974/9684087
    pdf.reset_index()
    for index, row in pdf.iterrows():
        day = row['date'].strftime("%a")
        date = row['date'].strftime("%Y-%m-%d")
        min_apparent = round(row["apparent_temperature_min"], 1)
        min_2m_above = round(row["temperature_2m_min"], 1)

        # Set row style
        color = ""
        icon = "&#127774;"  # Smiling sun: https://www.utf8icons.com/character/127774/sun-with-face
        if min_apparent <= 32 or min_2m_above <= 32:
            color = "style='color: blue; font-weight: bold;'"
            icon = "&#10052;"  # Snowflake: https://www.utf8icons.com/character/10052/snowflake

        html += f"""
                <tr {color}>
                    <td style='width: 20px;'>{icon}</td>
                    <td>{day}</td>
                    <td>{date}</td>
                    <td>{min_apparent}</td>
                    <td>{min_2m_above}</td>
                </tr>
        """

    html += '</table'

    return html


def get_freezing_days(pdf):
    # Filter the given pandas dataframe to only days where either temp column is freezing
    filtered_df = pdf.loc[(pdf['temperature_2m_min'] <= 32) | (pdf['apparent_temperature_min'] <= 32)]
    return filtered_df


if __name__ == '__main__':
    df = meteo_way()
    fdf = get_freezing_days(df)

    print(f'All days: ({len(df.index)})')
    print(df)

    print(f'Freezing days: ({len(fdf.index)})')
    print(fdf)

    # Only send an email if there are some freezing days
    if not fdf.empty:
        table = gen_html_table(df)
        send_email(table)
        print('Email sent!')
    else:
        print('No freezing days, quitting without sending an email.')
