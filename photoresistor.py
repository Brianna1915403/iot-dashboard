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

# Open both LEDs with GPIO output
def openlight():
    GPIO.output(LED, GPIO.HIGH)
    GPIO.output(LED2, GPIO.HIGH)

# Open LED with GPIO output
def solo_light(isOn):
    GPIO.output(LED3, GPIO.HIGH if isOn else GPIO.LOW)

# Close LED with GPIO output
def closesololight():
    GPIO.output(LED3, GPIO.LOW)

# Close both LEDs with GPIO output
def closelight():
    GPIO.output(LED, GPIO.LOW)
    GPIO.output(LED2, GPIO.LOW)
    print("not lit")