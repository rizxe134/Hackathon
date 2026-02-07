import RPi.GPIO as GPIO
import time

# Pin Definitions
TRIG = 23
ECHO = 24

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    # Ensure trigger is low
    GPIO.output(TRIG, False)
    time.sleep(0.1)

    # Send 10us pulse to Trigger
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Record the start and end time of the Echo pulse
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    # Calculate duration and distance
    pulse_duration = pulse_end - pulse_start
    # Speed of sound is ~34300 cm/s. Distance = (time * speed) / 2
    distance = pulse_duration * 17150
    return round(distance, 2)

try:
    print("Starting distance measurement...")
    while True:
        dist = get_distance()
        print(f"Distance: {dist} cm")
        time.sleep(1)

except KeyboardInterrupt:
    print("Measurement stopped by user")
    GPIO.cleanup()
