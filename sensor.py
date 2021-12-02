import serial
import time
from modules import read_serial
from modules import email
from database import database
import RPi.GPIO as GPIO
import smtplib, ssl, imaplib, email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

MotorA= 20
MotorB= 16
MotorEnable = 21
smtp_server = "smtp.gmail.com"
sender_email = "winone0619@gmail.com"
receiver_email = "winone0619@gmail.com"
password = "ImS19990619"

# ser = serial.Serial('/dev/ttyUSB0', 9600)

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MotorA, GPIO.OUT)
    GPIO.setup(MotorB, GPIO.OUT)
    GPIO.setup(MotorEnable, GPIO.OUT)

def turnOnFan() :
    GPIO.output(MotorA, GPIO.HIGH)
    GPIO.output(MotorB, GPIO.LOW)
    GPIO.output(MotorEnable, GPIO.HIGH)
def offFan():
        GPIO.output(MotorEnable, GPIO.LOW)

def sendEmail():
    message = MIMEMultipart("alternative")
    message["Subject"] = "Do you want to turn on the Fan?"
    message["From"] = sender_email
    message["To"] = receiver_email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    receiveEmail()

def receiveEmail():
 
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(receiver_email, password)
    mail.select('inbox')
    data = mail.search(None, '(FROM "winone0619@gmail.com")')
    ids = data[0] # data is a list.
    id_list = ids.split() # ids is a space separated string
    latest_email_id = id_list[-1]
    data = mail.fetch(latest_email_id, "(RFC822)") # fetch the email body (RFC822)             for the given ID
    bytes_data = data[0]
    email_message = email.message_from_bytes(bytes_data)
    response = ""
    time.sleep(10)
    if email_message != "":
        for part in email_message.walk():
            if part.get_content_type() == 'text/plain' or part.get_content_type()=="text/html":
                message = part.get_payload(decode=True)
                response = message.decode()
                if "YES" in response.upper():
                    # turnOnFan()
                    print("on")
                elif "NO" in response.upper():
                    # offFan()
                    print("off")
                break




setup()
sendEmail()
