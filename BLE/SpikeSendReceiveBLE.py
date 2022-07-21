'''
Based on SpikeSendReceive.py, this code makes the SPIKE into a force feedback steering wheel with gas and brake inputs. Oh, and 
it's Bluetooth.

To do
- Clean up the rumble code - right now there's a bug where it won't send any data while it's rumbling which means you're stuck 
  with the same speed and steering angle. Tried using the run_for_seconds() command in the Motor library from Spike and it just
  breaks (stops running the code and freezes) and then if running via the SPIKE app it says you need to update the hub OS again.
  A way to get past this might be to use Atlantis and async stuff.
- Move the BLE stuff into a library maybe so we can save ~100 lines?

Changelog
7/20/22
- Created file
'''

# Initialize the hub and get your imports
import bluetooth, hub, struct
from spike import Motor, ForceSensor
from micropython import const
from time import sleep


# Set up Bluetooth structure data, provided to us by the Mind Render folks
# This takes up a lot of the code, to skip to the main content jump to line ~150
_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)
_ADV_TYPE_UUID16_COMPLETE = const(0x3)
_ADV_TYPE_UUID32_COMPLETE = const(0x5)
_ADV_TYPE_UUID128_COMPLETE = const(0x7)
_ADV_TYPE_UUID16_MORE = const(0x2)
_ADV_TYPE_UUID32_MORE = const(0x4)
_ADV_TYPE_UUID128_MORE = const(0x6)
_ADV_TYPE_APPEARANCE = const(0x19)
_ADV_TYPE_SPECIFIC_DATA = const(0xFF)
_ADV_DATA_COMPANY_ID = const(0xFFFF)

def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None, appearance=0, free=None):
    payload = bytearray()

    def _append(adv_type, value):
        nonlocal payload
        payload += struct.pack("BB", len(value) + 1, adv_type) + value

    _append(
        _ADV_TYPE_FLAGS,
        struct.pack("B", (0x01 if limited_disc else 0x02) + (0x18 if br_edr else 0x04)),
    )

    if name:
        _append(_ADV_TYPE_NAME, name)

    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                _append(_ADV_TYPE_UUID16_COMPLETE, b)
            elif len(b) == 4:
                _append(_ADV_TYPE_UUID32_COMPLETE, b)
            elif len(b) == 16:
                _append(_ADV_TYPE_UUID128_COMPLETE, b)

    # org.bluetooth.characteristic.gap.appearance.xmlを参照してください。（デバイスの機能種別名）
    if appearance:
        _append(_ADV_TYPE_APPEARANCE, struct.pack("<h", appearance))

    return payload

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_MTU_EXCHANGED = const(21)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE,
)
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    bluetooth.FLAG_NOTIFY,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)

class BLEPeripheral:
    def __init__(self):
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._connections = set()
        self._payload = advertising_payload(name="wheel", services=[_UART_UUID]) # Change name here, keep it < 9 characters
        self._advertise()

    def is_connected(self):
        return len(self._connections) > 0

    def send(self, data):
        if self.is_connected():
            for handle in self._connections:
                self._ble.gatts_notify(handle, self._handle_rx, data)
                self._ble.gatts_notify(handle, self._handle_tx, data)

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
            print("Connection", conn_handle)

        elif event == _IRQ_CENTRAL_DISCONNECT:
            print("Disconnected")
            conn_handle, _, _ = data
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)

            #self._advertise()
            print("Disconnected", conn_handle)

        elif event == _IRQ_GATTS_WRITE:
            # print('Read')
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if value_handle == self._handle_rx:
                msg = float(value.decode()) # Decoding what we read and turning it into a decimal
                # print("received |", msg)
                steer.start(round(msg)) # Creating force feedback based on the input from MR
                sleep(.2)
                steer.start(round(-msg))
                sleep(.2)
                steer.stop()
                # print('0 steer')
                # steer.run_for_seconds(.3, round(msg))
                # print('1 steer')
                # steer.run_for_seconds(.3, round(-msg))
                # print('2 steer')
                # steer.stop()
                # print('done steer')

    def _advertise(self):
        self._ble.gap_advertise(500000, adv_data=self._payload)
        print("Advertise")



# This is where our code really begins, post BLE setup stuff
ble = BLEPeripheral()

# Quick light to make sure code is working
hub.display.clear()
sleep(.5)
hub.display.pixel(2,2,10)

# Set up the motor and force sensor on the Prime
steer = Motor('A') # Make sure to switch this and the next two to the right port
gas = ForceSensor('F')
brake = ForceSensor('E')
steer.set_stop_action('coast')
steer.stop()

while True:
    # We need to manually tell the SPIKE to send data but receiving happens automatically from setup
    # Note that if we're receiving the collision speed from MR, that is acted upon directly at line ~125
    payload = str(steer.get_position()) + "," + str(gas.get_force_percentage()) + "," + str(brake.get_force_percentage())
    ble.send(payload)
    print(payload)        # Uncomment if you think things are sus and wanna see what's being sent

# Sanity check
print('If this is printing then something is very wrong with the loop.')