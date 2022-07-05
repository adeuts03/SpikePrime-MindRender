'''
This code uses the ESP to send *and* receive data; it builds upon the send code in SpikeSend.py

To do
- clean up code
- make it faster
- comment things

Changelog
7/5/22
- Created file
'''

# initialize the hub and get your imports
from Backpack_Code import Backpack
import hub, math, utime, os, sys
from hub import motion
from spike import PrimeHub, Motor
from time import sleep



file = '''
print('testing')
'''
file = file.replace("\'",'"')

# make sure you change the port to wherever you have the ESP plugged in on the Prime
dongle = Backpack(hub.port.F, verbose = True) 

dongle.setup()
filename = 'test.py'
dongle.load(filename,file)
reply = dongle.get(filename)

if (reply == file):
    print("Testing done.")
print("_________________________________________________________")


# on first run of this code, we need to get the ESP to import our send library
dongle.ask('from esp_send import send_message')
# we then need to set up our connection over wifi - change the IP address address and port below
# do NOT change anything else - leave the quotes, slashes, and commas the way they are
#                                   IP          port 
dongle.ask('x = send_message(\"10.247.98.69\", 21024)')

    

hub.display.clear()
utime.sleep(.5)
hub.display.pixel(2,2,10)

hub = PrimeHub()

dongle.ask('import socket')
dongle.ask('UDP_IP = "10.245.81.17"')
dongle.ask('UDP_PORT = 21024')
dongle.ask('sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)')
dongle.ask('sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)')
dongle.ask('sock.bind((UDP_IP, UDP_PORT))')
testing = []

motor = Motor('E')

while True:
    print('----------pre read-------------')
    hub._light_matrix.off()
    ESPraw = ""
    dongle.ask('data, addr = sock.recvfrom(1024)')
    dongle.ask("data = data.decode('UTF-8')")
    ESPraw = dongle.ask('print(data)')
    ESPclean = ""
    if not (ESPraw == ""):
        for i in ESPraw:
            if i.isdigit():
                ESPclean = ESPclean + i
            elif (i == "."):
                ESPclean = ESPclean + i
        hub._light_matrix.set_pixel(4,4,99)
        print(float(ESPclean))
        sleep(.1)
        motor.start(round(float(ESPclean)))
    print('----------post read-------------')
        
    #empty array to hold acceleration values
    accs = []
    
    #wait until left button is pressed
    #hub._left_button.wait_until_pressed()
    if hub._left_button.is_pressed():
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
        
    
        message = "x.send(\'" + str(acc) + "\')"
        dongle.ask(message)
        print(message)
        
        #display an arrow on hub display with increasing brightness
        for i in range(11):
            hub.light_matrix.show_image('ARROW_N', brightness=i*10)
            utime.sleep(.1)

print('line end')