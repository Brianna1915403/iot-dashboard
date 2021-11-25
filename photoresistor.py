import RPi.GPIO as GPIO
# import serial
from modules import email
from database import database

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
db = database("_data.db")

LED = 12
LED2 = 18
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)


def openlight():
    GPIO.output(LED, GPIO.HIGH)
    GPIO.output(LED2, GPIO.HIGH)
    print("lit")

def closelight():
    GPIO.output(LED, GPIO.LOW)
    GPIO.output(LED2, GPIO.LOW)
    print("not lit")