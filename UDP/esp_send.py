import network, socket, time

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
        
    def send(self, msg):
        msg = bytes(msg, "utf-8")
        
        self.s.send(msg)

    def close():
        self.s.close()


