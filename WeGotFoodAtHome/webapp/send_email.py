import smtplib, ssl
import os
from dotenv import find_dotenv, load_dotenv


def send_verify(email,url,message):
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)
    em_password = os.getenv("em_password")
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = "we.gotfood.at.homes@gmail.com"
    receiver_email = email
    password = em_password

    message = f"""\
    Subject: The Kitchen {message} \n{url}."""

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)