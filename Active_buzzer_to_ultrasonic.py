from gpiozero import DistanceSensor, Buzzer
from time import sleep

# Define pins
# echo, trigger, and buzzer
sensor = DistanceSensor(echo=24, trigger=23)
buzzer = Buzzer(25)

# Safety threshold in meters
ALARM_DISTANCE = 0.3  # 30 centimeters

print("Ultrasonic Alarm Active...")

try:
    while True:
        # Distance is returned in meters (0.0 to 1.0)
        dist = sensor.distance
        print(f"Distance: {dist*100:.1f} cm")

        if dist < ALARM_DISTANCE:
            print("!!! TOO CLOSE !!!")
            buzzer.on()
            sleep(0.1) # Rapid beeping or steady tone
            buzzer.off()
        else:
            buzzer.off()
            
        sleep(0.1)

except KeyboardInterrupt:
    print("\nAlarm stopped by user")
    buzzer.off()
