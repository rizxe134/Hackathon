sudo apt-get update
sudo apt-get install -y pigpio python3-pigpio python3-rpi.gpio
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

import time
import pigpio
import RPi.GPIO as GPIO

# -----------------------
# GPIO pins (BCM mode)
# -----------------------
TRIG = 23
ECHO = 24
SERVO_GPIO = 18

# -----------------------
# Behavior tuning
# -----------------------
LOCK_DISTANCE_CM = 40.0      # if object is closer than this, lock camera to center
UNLOCK_DISTANCE_CM = 50.0    # hysteresis: must be farther than this to resume scanning
CENTER_ANGLE = 90

SCAN_MIN_ANGLE = 30
SCAN_MAX_ANGLE = 150
SCAN_STEP_DEG = 2            # how many degrees per update when scanning

# Scan speed control
BASE_SCAN_DELAY = 0.03       # seconds between servo updates (smaller = faster)
FAR_DISTANCE_CM = 150.0      # used to scale scan speed

# Ultrasonic reading
READS_TO_MEDIAN = 5          # take multiple reads and use median for stability
MAX_VALID_CM = 400.0
MIN_VALID_CM = 2.0

# -----------------------
# Servo pulse mapping
# -----------------------
# Typical safe pulse widths; adjust if your servo range is smaller/larger.
MIN_US = 600
MAX_US = 2400

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def angle_to_pulse(angle_deg: float) -> int:
    angle_deg = clamp(angle_deg, 0, 180)
    return int(MIN_US + (angle_deg / 180.0) * (MAX_US - MIN_US))

def median(values):
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 == 1 else (s[mid - 1] + s[mid]) / 2.0

# -----------------------
# HC-SR04 distance read
# -----------------------
def read_distance_cm(timeout_s=0.03) -> float | None:
    # Trigger a 10us pulse
    GPIO.output(TRIG, False)
    time.sleep(0.0002)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Wait for echo to go high
    start = time.time()
    while GPIO.input(ECHO) == 0:
        if time.time() - start > timeout_s:
            return None

    pulse_start = time.time()

    # Wait for echo to go low
    while GPIO.input(ECHO) == 1:
        if time.time() - pulse_start > timeout_s:
            return None

    pulse_end = time.time()

    # Distance: speed of sound ~34300 cm/s, distance is half the travel
    pulse_duration = pulse_end - pulse_start
    distance_cm = (pulse_duration * 34300.0) / 2.0

    if distance_cm < MIN_VALID_CM or distance_cm > MAX_VALID_CM:
        return None
    return distance_cm

def stable_distance_cm() -> float | None:
    reads = []
    for _ in range(READS_TO_MEDIAN):
        d = read_distance_cm()
        if d is not None:
            reads.append(d)
        time.sleep(0.01)
    if not reads:
        return None
    return median(reads)

# -----------------------
# Main
# -----------------------
def main():
    # GPIO setup for ultrasonic
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.output(TRIG, False)

    # pigpio for servo
    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError("pigpio daemon not running. Try: sudo systemctl start pigpiod")

    # Start centered
    pi.set_servo_pulsewidth(SERVO_GPIO, angle_to_pulse(CENTER_ANGLE))
    time.sleep(0.5)

    angle = CENTER_ANGLE
    direction = 1  # +1 or -1
    locked = False

    print("Running: scanning camera until object gets close, then lock to center.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            dist = stable_distance_cm()

            # Decide lock/unlock with hysteresis
            if dist is not None:
                if not locked and dist < LOCK_DISTANCE_CM:
                    locked = True
                elif locked and dist > UNLOCK_DISTANCE_CM:
                    locked = False

            if locked:
                # Lock to center
                angle = CENTER_ANGLE
                pi.set_servo_pulsewidth(SERVO_GPIO, angle_to_pulse(angle))
                # Update slower while locked
                time.sleep(0.08)
            else:
                # Scan left-right
                angle += direction * SCAN_STEP_DEG
                if angle >= SCAN_MAX_ANGLE:
                    angle = SCAN_MAX_ANGLE
                    direction = -1
                elif angle <= SCAN_MIN_ANGLE:
                    angle = SCAN_MIN_ANGLE
                    direction = 1

                pi.set_servo_pulsewidth(SERVO_GPIO, angle_to_pulse(angle))

                # Optional: scan faster when something is closer (but not in lock zone)
                delay = BASE_SCAN_DELAY
                if dist is not None:
                    # scale delay between BASE_SCAN_DELAY and ~3x BASE_SCAN_DELAY
                    # farther -> slower, closer -> faster
                    scaled = clamp(dist / FAR_DISTANCE_CM, 0.15, 1.0)
                    delay = BASE_SCAN_DELAY * (0.6 + 1.8 * scaled)

                time.sleep(delay)

            # Debug print (lightweight)
            if dist is None:
                print(f"\rDist: --- cm | locked: {locked} | angle: {angle:3d}   ", end="", flush=True)
            else:
                print(f"\rDist: {dist:6.1f} cm | locked: {locked} | angle: {angle:3d}   ", end="", flush=True)

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        # Stop servo pulses and cleanup
        pi.set_servo_pulsewidth(SERVO_GPIO, 0)
        pi.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
