'''
To do
- name this code
- clean up code in general
- comment out code and describe what it's doing
- add debug things (the first chunk of code is essentially a test to make sure serial is working, 
  that can probably be thrown into a debug section that can be turned on/off)
'''



# Make sure you have Backpack_Code.py "installed" (aka saved) on the Spike and send_udp.py installed on the ESP

import os
from Backpack_Code import Backpack
import sys

#initialize hub

import hub, math, utime
from hub import motion
from spike import PrimeHub



file = '''
print('testing')
'''
file = file.replace("\'",'"')

dongle = Backpack(hub.port.F, verbose = True) 

dongle.setup()
filename = 'test.py'
dongle.load(filename,file)
reply = dongle.get(filename)
print(reply == file)


print("Testing done.")
print("_________________________________________________________")



dongle.ask('from esp_send import send_message')
dongle.ask('x = send_message(\"10.245.95.56\", 21024)')

# dongle.ask('x.send(\'123\')')
# utime.sleep(5)

iterations = 0
move = 1300
while (iterations < 2):
    print("New iteration, get ready to move.")
    print("3")
    utime.sleep(.1)
    print("2")
    utime.sleep(.1)
    print("1")
    utime.sleep(.1)
    print("Move!")
    
    utime.sleep(.1)
    print('Processing...')
    iterations += 1
    move = move + iterations
    message = "x.send(\'" + str(move) + "\')"
    print("message is", message)
    dongle.ask(message)
    utime.sleep(.1)

print("End of program. ***NOT*****")

hub.display.clear()
utime.sleep(.5)
hub.display.pixel(2,2,10)

hub = PrimeHub()

while True:
    #empty array to hold acceleration values
    accs = []
    
    #wait until left button is pressed
    hub._left_button.wait_until_pressed()
    while hub._left_button.is_pressed():
        #instantaneous x y z acceleration
        (a_x, a_y, a_z) = motion.accelerometer()
        
        #take magnitude of x and y acceleration (since on flat table) and add to array
        mag = math.sqrt(a_x**2 + a_y**2)
        accs.append(mag)
        
        #samples acceleration every 0.01 seconds
        utime.sleep(0.01)
    
    #find maximum acceleration while left button was held
    acc = max(accs)
    
    print(accs)
    print(acc)
    message2 = "x.send(\'" + str(acc) + "\')"
    dongle.ask(message2)
    print(message2)
    
    #display an arrow on hub display with increasing brightness
    for i in range(11):
        hub.light_matrix.show_image('ARROW_N', brightness=i*10)
        utime.sleep(.1)
        

