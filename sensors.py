import time
from gpiozero import Buzzer
import RPi.GPIO as GPIO
import smtplib, ssl, imaplib, email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

MotorA= 20
MotorB= 16
MotorEnable = 21
smtp_server = "smtp.office365.com"
sender_email = "vanier.1915403@hotmail.com"
receiver_email = "winone0619@gmail.com"
password = "DumpEmail2"

maxTemp = 22


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
    with smtplib.SMTP_SSL(smtp_server, 587, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    receiveEmail()

def receiveEmail():
    response = ""
    while response == "" :
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(receiver_email, password)
        mail.select('inbox')
        status, data = mail.search(None, '(FROM "winone0619@gmail.com")')
        ids = data[0] # data is a list.
        id_list = ids.split() # ids is a space separated string
        latest_email_id = id_list[-1]
        result, data = mail.fetch(latest_email_id, "(RFC822)") # fetch the email body (RFC822)             for the given ID
        result, bytes_data = data[0]
        email_message = email.message_from_bytes(bytes_data)
        response = ""
        
        if email_message != "":
            for part in email_message.walk():
                if part.get_content_type() == 'text/plain' or part.get_content_type()=="text/html":
                    message = part.get_payload(decode=True)
                    response = message.decode()
                    if "YES" in response.upper():
                        turnOnFan()
                    elif "NO" in response.upper():
                        offFan()
                    break


setup()
while 1:
    temperature = sensor.temperature
    humidity = sensor.humidity
    if humidity is not None and temperature is not None:
        print('Temp={0:0.1f}*C Humidity={1:0.1f}%'.format(temperature,humidity))
        if temperature >= maxTemp:
            sendEmail()
    else:
        print('Failed to read')
    time.sleep(2)
    
    

