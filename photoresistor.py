# import RPi.GPIO as GPIO
# import time, os
# from decouple import config
# from modules import read_serial
# from modules import email
# from database import database

# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BCM)

# LED = 12
# LED2 = 18
# GPIO.setup(LED, GPIO.OUT)
# GPIO.setup(LED2, GPIO.OUT)

# db = database("_data.db")
# db.open()
# usr_row = db.select("user", where = f"id = {config('CURRENT_USER')}")
# db.close()
# print(usr_row)
# threshold = usr_row[0][4]
# serial = read_serial("/dev/ttyUSB0", 115200)

# class photoresistor:
#     def run():
#         print(usr_row[0][2])
#         mail = email()
#         mail.send(usr_row[0][2], "Its lit")
#         # while True:
#         #     if int(serial.read()) < threshold:
#         #         GPIO.output(LED, GPIO.LOW)
#         #         GPIO.output(LED2, GPIO.LOW)
#         #         print(read_serial("/dev/ttyUSB0", 115200))
#         #     else:
#         #         GPIO.output(LED, GPIO.HIGH)
#         #         GPIO.output(LED2, GPIO.HIGH)



# photoresistor.run()