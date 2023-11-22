import smtplib
import os

sender = "Private Person <mailtrap@nbrinton.dev>"
receiver = "A Test User <nab.natethegreat@gmail.com>"

message = f"""\
Subject: Hi Mailtrap
To: {receiver}
From: {sender}

This is a test e-mail message."""

with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
    server.connect("live.smtp.mailtrap.io", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(os.environ["MAILTRAP_SMTP_USERNAME"], os.environ["MAILTRAP_SMTP_PASSWORD"])
    server.sendmail(sender, receiver, message)