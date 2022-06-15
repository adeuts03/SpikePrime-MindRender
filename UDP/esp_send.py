from machine import Pin
import network, socket, time
pin = machine.Pin(2, machine.Pin.OUT)

class send_message():
    def __init__(self, IP, port):
        wlan = network.WLAN(network.STA_IF)

        if not wlan.isconnected():
            wlan.active(True)

            # Try to connect to Tufts_Wireless:
            ssid = "Tufts_Wireless"
            print("Connecting to {}...".format(ssid))
            wlan.connect(ssid)

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.connect((IP, port))
        
        print("Connected!")
        print("IP address:", wlan.ifconfig()[0])
        
    def send(self, msg):
        msg = bytes(msg, "utf-8")
        
        self.s.send(msg)

        for i in range(3):
            pin.value(0)
            time.sleep(.025)
            pin.value(1)
            time.sleep(.025)

    def close(self):
        self.s.close()
