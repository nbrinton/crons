import smtplib
import os
import requests
import mailtrap as mt

# Open Meteo variables
om_base_url = 'https://api.open-meteo.com'
om_version = 'v1'


def send_email():
    # create mail object
    mail = mt.Mail(
        sender=mt.Address(email="mailtrap@nbrinton.dev", name="Mailtrap Test"),
        to=[mt.Address(email="nathanbrinton@outlook.com")],
        subject="You are awesome!",
        text="Congrats for sending test email with Mailtrap!",
    )

    # create client and send
    # client = mt.MailtrapClient(token="5c5e0bea1d755ee837a172f8272d207f")
    client = mt.MailtrapClient(token=os.environ["MAILTRAP_SMTP_PASSWORD"])
    client.send(mail)


# def send_email():
#     sender = "Private Person <mailtrap@nbrinton.dev>"
#     receiver = "A Test User <nab.natethegreat@gmail.com>"
#
#     message = f"""\
#         Subject: Hi Mailtrap
#         To: {receiver}
#         From: {sender}
#
#         This is a test e-mail message."""
#
#     with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
#         server.connect("live.smtp.mailtrap.io", 587)
#         # server.ehlo()
#         server.starttls()
#         # server.ehlo()
#         server.login(os.environ["MAILTRAP_SMTP_USERNAME"], os.environ["MAILTRAP_SMTP_PASSWORD"])
#         server.sendmail(sender, receiver, message)


# Mailtrap variables
# sender = "Private Person <mailtrap@nbrinton.dev>"
# receiver = "A Test User <nab.natethegreat@gmail.com>"


# def send_email(fdays):
#     sender = "Private Person <mailtrap@nbrinton.dev>"
#     receiver = "A Test User <nab.natethegreat@gmail.com>"
#
#     message = f"""\
#     Subject: Hi Mailtrap
#     To: {receiver}
#     From: {sender}
#
#     This is a test e-mail message."""
#     # for fday in fdays:
#     #     message += f'{fday[0]}: {fday[1]}/'
#
#     with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
#         server.connect("live.smtp.mailtrap.io", 587)
#         server.ehlo()
#         server.starttls()
#         server.ehlo()
#         server.login(os.environ["MAILTRAP_SMTP_USERNAME"], os.environ["MAILTRAP_SMTP_PASSWORD"])
#         server.sendmail(sender, receiver, message)


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

    # TODO: Trying to programmatically grab the array for each key to then combine using zip instead of manually
    #  specifying keys
    # for k, v in j.items():
    #     data[k] =

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
        send_email()
        # send_email(freezing_days)
        # print('TODO: send email')

# sender = "Private Person <mailtrap@nbrinton.dev>"
# receiver = "A Test User <nab.natethegreat@gmail.com>"
#
# message = f"""\
# Subject: Hi Mailtrap
# To: {receiver}
# From: {sender}
#
# This is a test e-mail message."""
#
# with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
#     server.connect("live.smtp.mailtrap.io", 587)
#     # server.ehlo()
#     server.starttls()
#     # server.ehlo()
#     server.login(os.environ["MAILTRAP_SMTP_USERNAME"], os.environ["MAILTRAP_SMTP_PASSWORD"])
#     server.sendmail(sender, receiver, message)
