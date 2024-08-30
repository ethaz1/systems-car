import RPi.GPIO as GPIO          
from time import sleep
import evdev
from enum import Enum, auto
import numpy as np

# PWM pins, for controlling speed
L_ENA = 14
R_ENA = 17

# left motor
L_IN1 = 27
L_IN2 = 22

# right motor
R_IN1 = 15
R_IN2 = 18


#### Motor configuration ###
GPIO.setmode(GPIO.BCM)

GPIO.setup(L_ENA, GPIO.OUT)
GPIO.setup(L_IN1, GPIO.OUT)
GPIO.setup(L_IN2, GPIO.OUT)

GPIO.setup(R_ENA, GPIO.OUT)
GPIO.setup(R_IN1, GPIO.OUT)
GPIO.setup(R_IN2, GPIO.OUT)

GPIO.output(L_IN1, GPIO.LOW)
GPIO.output(L_IN2, GPIO.LOW)
GPIO.output(R_IN1, GPIO.LOW)
GPIO.output(R_IN2, GPIO.LOW)

PL=GPIO.PWM(L_ENA, 1000)
PR=GPIO.PWM(R_ENA, 1000)

speed = 0
YIELD_TIME = 0.25 # how long each key press will run the command before returning to the loop

PL.start(speed)
PR.start(speed)
##############################



### CONTROLLER ###
class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()
    NEITHER = auto()

XBOX_CONTROLLER_FILE = "/dev/input/event4"
CURRENT_DIRECTION = Direction.NEITHER
ANALOG_STICK_CENTRE = 32767
ANALOG_STICK_LOWER_DEADZONE = -0.1
ANALOG_STICK_UPPER_DEADZONE = 0.1
REVERSING = False
TRIGGER_OFFSET = 900 # how far you need to push down on the trigger to get to full speed. 1024 is all the way, less means not all the way.

g_is_running = True      # flag for whether the app should stop listening to keyboard commands and stop


def backward():
    GPIO.output(L_IN1, GPIO.HIGH)
    GPIO.output(R_IN1, GPIO.HIGH)
    print("motors are going: forwards")
    
def forward():
    GPIO.output(L_IN2, GPIO.HIGH)
    GPIO.output(R_IN2, GPIO.HIGH)
    print("motors are going: backwards")

def left():
    GPIO.output(R_IN2, GPIO.HIGH)
    print("motors are going: left")

def right():
    GPIO.output(L_IN2, GPIO.HIGH)
    print("motors are going: right")
    
def set_speed(speed):
    PL.start(speed)
    PR.start(speed)
    print(f"new speed {speed}")
    
def stop_all():
    GPIO.output(L_IN1, GPIO.LOW)
    GPIO.output(R_IN1, GPIO.LOW)
    GPIO.output(L_IN2, GPIO.LOW)
    GPIO.output(R_IN2, GPIO.LOW)
                       
def cleanup():
    GPIO.cleanup()
    print("cleaned up. stopping...")
    exit()
    
def map_values(value, in_min, in_max, out_min, out_max): # returns an interporlated value that is now between out_min and out_max
    return np.interp(value, [in_min, in_max], [out_min, out_max])
    
def get_acceleration_power(value):
    global speed
    speed = round(map_values(value, 0, TRIGGER_OFFSET, 0, 100))
    
def get_analog_stick_direction(value):
    global CURRENT_DIRECTION # this shouldn't be global, but this function wants to invent a local one out of thin air
    
    x_axis = (value - ANALOG_STICK_CENTRE) / ANALOG_STICK_CENTRE
    # for turning
    if (x_axis > ANALOG_STICK_UPPER_DEADZONE):
        CURRENT_DIRECTION = Direction.RIGHT
    elif (x_axis < ANALOG_STICK_LOWER_DEADZONE):
        CURRENT_DIRECTION = Direction.LEFT
    else:     
        CURRENT_DIRECTION = Direction.NEITHER  
    #print(CURRENT_DIRECTION.name)
        
def move_motors():
    global CURRENT_DIRECTION
    global REVERSING
    
    stop_all()
    
    if (CURRENT_DIRECTION == Direction.NEITHER):
        if (REVERSING):
            backward()
        else:
            forward()
    elif (CURRENT_DIRECTION == Direction.LEFT):
        left()
    elif (CURRENT_DIRECTION == Direction.RIGHT):
        right()
        
    set_speed(speed)

### MAIN ###
print("You can press the X button on your controler to stop at any time. do not force stop the application as the cleanup procedure won't run.")



while (g_is_running):


    for event in evdev.InputDevice(XBOX_CONTROLLER_FILE).read_loop():
        #print(f"Direction: {CURRENT_DIRECTION.name}, Speed:{speed}, Backwards? {REVERSING}")
        move_motors()
        
        # analog sticks and triggers
        if event.type == evdev.ecodes.EV_ABS:
            
            if event.code == evdev.ecodes.ABS_X: # left and right on the left analog stick
                get_analog_stick_direction(event.value)
                
            if event.code == evdev.ecodes.ABS_GAS: # up and down on the right trigger
                get_acceleration_power(event.value)
                REVERSING = False
                
            if event.code == evdev.ecodes.ABS_BRAKE: # up and down on the left trigger
                get_acceleration_power(event.value)
                REVERSING = True
        
        # buttons
        if event.type == evdev.ecodes.EV_KEY:
            
            if event.code == evdev.ecodes.BTN_NORTH: # X button (incorrectly mapped as north, oops!)
                if event.value == 1:
                    cleanup()
            
    

cleanup()


