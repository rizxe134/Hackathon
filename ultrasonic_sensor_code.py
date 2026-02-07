import RPi.GPIO as GPIO
import time

TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.05) # Settling time

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Initialize variables to avoid 'UnboundLocalError'
    pulse_start = time.time()
    pulse_end = time.time()

    # Timeout logic: if it takes > 0.1s, something is wrong
    timeout = time.time() + 0.1

    # Wait for Echo to go HIGH
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if pulse_start > timeout:
            return None # Out of range or wiring error

    # Wait for Echo to go LOW
    timeout = time.time() + 0.1
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if pulse_end > timeout:
            return None

    duration = pulse_end - pulse_start
    distance = duration * 17150
    return round(distance, 2)

try:
    print("Measurement started...")
    while True:
        dist = get_distance()
        if dist is not None:
            print(f"Distance: {dist} cm")
        else:
            print("Out of range / Reading error")
        time.sleep(0.5)

except KeyboardInterrupt:
    GPIO.cleanup()
