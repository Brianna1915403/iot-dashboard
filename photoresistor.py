import RPi.GPIO as GPIO
# import serial
from modules import email
from database import database

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
db = database("_data.db")

LED = 12
LED2 = 18
LED3 = 5
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)
GPIO.setup(LED3, GPIO.OUT)


def openlight():
    GPIO.output(LED, GPIO.HIGH)
    GPIO.output(LED2, GPIO.HIGH)
    print("lit")

def solo_light(isOn):
    GPIO.output(LED3, GPIO.HIGH if isOn else GPIO.LOW)

def closesololight():
    GPIO.output(LED3, GPIO.LOW)

def closelight():
    GPIO.output(LED, GPIO.LOW)
    GPIO.output(LED2, GPIO.LOW)
    print("not lit")