import serial
import email, smtplib, imaplib, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config
from database import database

class email:
    def __init__(self) -> None:
        self.email = f"{config('EMAIL')}"
        self.password = f"{config('PASSWORD')}"
        self.mail_server = 'outlook.office365.com' 
        self.mail_server_port_send = 583    
        self.mail_server_port_read = 993   

    def command(msg):
        switch = {}
        return switch.get(msg.partition('\n')[0].strip().upper(), "INVALID COMMAND")

    def send(self, receiver, message):
        msg = MIMEMultipart("alternative")
        msg['From'] = self.email
        msg['To'] = receiver
        msg['Subject'] = "SMART HOME"
        msg.attach(MIMEText(message, "plain"))

        mail = smtplib.SMTP(self.mail_server, self.mail_server_port_send)
        mail.ehlo()
        mail.starttls()
        mail.ehlo()
        mail.login(self.email, self.password)
        mail.sendmail(self.email, self.receiver, msg.as_string())
        mail.quit()

    def read(self):
        mail = imaplib.IMAP4_SSL(self.mail_server, self.mail_server_port_read)
        mail.login(self.email, self.password)
        mail.select('inbox')

        # --- WATCH START ---
        while True:
            status, data = mail.search(None, 'UNSEEN')
            mail_ids = []

            for block in data:
                mail_ids += block.split()
            
            if(mail_ids):
                latest_email = mail_ids[-1]
                status, data = mail.fetch(latest_email, '(RFC822)')

            for response_part in data:
                if isinstance(response_part, tuple):
                    message = email.message_from_bytes(response_part[1])    
                mail_from = message['from']
                mail_subject = message['subject']
                if message.is_multipart():
                    mail_content = ''
                    for part in message.get_payload():
                        if part.get_content_type() == 'text/plain':
                            mail_content += part.get_payload()
                else:
                    mail_content = message.get_payload()

            if ("SMART HOME" not in mail_subject):
                continue

            print(f'From: {mail_from}')
            print(f'Subject: {mail_subject}')
            print(f'Content: {mail_content}')

            if (not self.command(mail_content)):
                mail.close()
                mail.logout()
                return "EXIT"
            else:
                print(self.command(mail_content))
        # --- WATCH END ---


class rfid:
    def __init__(self, tag) -> None:
        self.tag = tag

    def check_access(self):
        pass

    def submit_record(self):
        pass


class read_serial:
    def __init__(self, port, timing) -> None:
        self.port = port
        self.timing = timing

    def read (self):
        ser = serial.Serial(self.port, self.timing, 8, 'N', 1, timeout=1)

        while 1:
            if(ser.in_waiting > 0):
                ser.readline().decode('utf-8').rstrip()
                