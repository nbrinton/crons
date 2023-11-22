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


if __name__ == '__main__':
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
