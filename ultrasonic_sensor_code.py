import RPi.GPIO as GPIO
import time

# Set GPIO Mode (BCM refers to the Broadcom SOC channel numbers)
GPIO.setmode(GPIO.BCM)

# Define pins
TRIG = 23
ECHO = 24

print("Distance measurement in progress...")

# Setup pins
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    # Ensure sensor is settled
    GPIO.output(TRIG, False)
    time.sleep(0.1)

    # Send a 10us pulse to TRIG
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Record the start and end of the ECHO pulse
    pulse_start = time.time()
    pulse_end = time.time()

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    # Calculate distance
    pulse_duration = pulse_end - pulse_start
    # Speed of sound is 34300 cm/s. We divide by 2 (there and back)
    distance = (pulse_duration * 34300) / 2
    return round(distance, 2)

try:
    while True:
        dist = get_distance()
        print(f"Distance: {dist} cm")
        time.sleep(1)

except KeyboardInterrupt:
    print("Measurement stopped by user")
    GPIO.cleanup()
