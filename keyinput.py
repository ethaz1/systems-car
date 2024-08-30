# DESCRIPTION
# drives the motors using the WASD keys.

import RPi.GPIO as GPIO          
from time import sleep
import keyboard

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

speed = 100
YIELD_TIME = 0.25 # how long each key press will run the command before returning to the loop

PL.start(speed)
PR.start(speed)
##############################


g_is_running = True      # flag for whether the app should stop listening to keyboard commands and stop


def backward(t):
    GPIO.output(L_IN1, GPIO.HIGH)
    GPIO.output(R_IN1, GPIO.HIGH)
    print("motors are going: backward")
    sleep(t)
    GPIO.output(L_IN1, GPIO.LOW)
    GPIO.output(R_IN1, GPIO.LOW)
    
def forward(t):
    GPIO.output(L_IN2, GPIO.HIGH)
    GPIO.output(R_IN2, GPIO.HIGH)
    print("motors are going: forward")
    sleep(t)
    GPIO.output(L_IN2, GPIO.LOW)
    GPIO.output(R_IN2, GPIO.LOW)

def left(t):
    GPIO.output(R_IN2, GPIO.HIGH)
    print("motors are going: left")
    sleep(t)
    GPIO.output(R_IN2, GPIO.LOW)

def right(t):
    GPIO.output(L_IN2, GPIO.HIGH)
    print("motors are going: right")
    sleep(t)
    GPIO.output(L_IN2, GPIO.LOW)


### MAIN ###
print("You can press 'x' to stop at any time. do not force stop the application as the cleanup procedure won't run.")
while(g_is_running):
    
    if keyboard.is_pressed('x'):
        g_is_running = False  
    elif keyboard.is_pressed('a'):
        left(YIELD_TIME)
    elif keyboard.is_pressed('d'):
        right(YIELD_TIME)
    elif keyboard.is_pressed('w'):
        forward(YIELD_TIME)
    elif keyboard.is_pressed('s'):
        backward(YIELD_TIME)



GPIO.cleanup()
print("cleaned up. stopping...")


