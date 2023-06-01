import RPi.GPIO as GPIO
import time

TRIG_PIN = 23
ECHO_PIN = 24

SPEED_OF_SOUND = 34300

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

LOWER_THRESHOLD = 10
UPPER_THRESHOLD = 100

def get_distance():
  """
  Measures distance using ultrasonic sensor
  """
  
  GPIO.output(TRIG_PIN, False)
  time.sleep(0.002)
  GPIO.output(TRIG_PIN, True)
  time.sleep(0.00001)
  GPIO.output(TRIG_PIN, False)

  pulse_start = time.time()

  while GPIO.input(ECHO_PIN) == 0:
    pass
  pulse_start = time.time()

  while GPIO.input(ECHO_PIN) == 1:
    pass
  pulse_end = time.time()

  pulse_duration = pulse_end - pulse_start
  distance = (pulse_duration * SPEED_OF_SOUND) / 2
  return distance

def detect_motion():
  previous_distance = get_distance()
  while True:
    current_distance = get_distance()
    change = abs(current_distance - previous_distance)
    if change <= UPPER_THRESHOLD and change >= LOWER_THRESHOLD:
      print("Motion detected!")
      print("Distance:", change)
      
    previous_distance = current_distance
    time.sleep(0.1)  
  GPIO.cleanup()


if __name__ == "__main__":
  detect_motion()
