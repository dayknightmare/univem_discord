from email.message import EmailMessage
from email.utils import formataddr
from email.header import Header
from dotenv import load_dotenv
import smtplib, ssl
import csv
import os


load_dotenv()

def open_mail_file() -> list:
    mails = []

    with open('./mail.csv') as f:
        data = csv.reader(f)

        for i in data:
            mails.append(i[0].lower())

    return list(set(mails))


class Mail:
    def __init__(self):
        try:
            self.port = int(os.getenv('MAIL_PORT'))

        except ValueError:
            return

        self.mail = os.getenv('MAIL_EMAIL')
        self.password = os.getenv('MAIL_PASSWORD')
        self.host = os.getenv('MAIL_HOST')


    def __mail_ssl(self):
        context = ssl.create_default_context()

        self.server = smtplib.SMTP_SSL(self.host, self.port, context=context)
        self.server.login(self.mail, self.password)


    def __mail_starttls(self):
        context = ssl.create_default_context()

        try:
            self.server = smtplib.SMTP(self.host, self.port)
            self.server.ehlo()
            self.server.starttls(context=context)
            self.server.ehlo()
            self.server.login(self.mail, self.password)

        except Exception as e:
            print(e)


    def send_mail(self, to: str, email: str, subject: str):
        try:
            if self.port == 465:
                self.__mail_ssl()

            else:
                self.__mail_starttls()

            print(f"Enviando email para {to}")

            msg = EmailMessage()
            msg['From'] = formataddr((str(Header('Unides', 'utf-8')), self.mail))
            msg['Subject'] = subject
            msg['To'] = to
            msg.set_content(email)

            self.server.send_message(msg)

            print(f"Enviando com sucesso")

        except Exception as e:
            print(e)
            print('Error to send email')
