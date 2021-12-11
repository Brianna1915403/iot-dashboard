import RPi.GPIO as GPIO
from time import sleep

MotorA = 20
MotorB = 16
MotorEnable = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(MotorA, GPIO.OUT)
GPIO.setup(MotorB, GPIO.OUT)
GPIO.setup(MotorEnable, GPIO.OUT)

def setup():    
    pass

def loop() :
    GPIO.output(MotorA, GPIO.HIGH)
    GPIO.output(MotorB, GPIO.LOW)
    GPIO.output(MotorEnable, GPIO.HIGH)
    
    GPIO.output(MotorEnable, GPIO.LOW)

def destroy():
    GPIO.cleanup()

setup()
loop()
