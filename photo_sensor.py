from time import sleep
import RPi.GPIO as GPIO, time
import logging
import thread

class photo_sensor:
    log = None
    GPIO = None
    pin = 0
    light_value = 0
    delay = 0
    def __init__(self):
        self.log = logging.getLogger()
        logging.basicConfig()
        self.log.setLevel(logging.DEBUG)
        self.GPIO = GPIO.setmode(GPIO.BOARD)
        self.log.debug('GPIO.BOARD')
        thread.start_new(self.init,(7,))
        
    def init(self,pin = 7):
        self.log.debug('executing init thread')
    # Define function to measure charge time
        while True:
            measurement = 0
            # Discharge capacitor
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(0.1)

            GPIO.setup(pin, GPIO.IN)
            # Count loops until voltage across
            # capacitor reads high on GPIO
            while (GPIO.input(pin) == GPIO.LOW):
                measurement += 1
                if measurement >= 10000:
                    break
                else:
                    sleep(0.001)
            self.light_value = measurement
            delay = 30 - (measurement/1000)
            #self.log.debug('light_value: '+str(self.light_value))
            sleep(delay)


    # Main program loop
    def get_value(self):
        return self.light_value # Measure timing using GPIO4
