'''
To do
- clean up code

Changelog
6/28/22
- Created new file based off of SpikeSend.py but uses BLE protocol to communicate with MR
'''



import bluetooth, hub, math, utime, struct
from spike import PrimeHub
from math import *
from hub import motion
from micropython import const


_ADV_TYPE_FLAGS = const(0x01)            # GAP通信における制御情報
_ADV_TYPE_NAME = const(0x09)            # デバイスの名称(完全版)(28Bを超えるなら0x08の短縮名称を使う)
_ADV_TYPE_UUID16_COMPLETE = const(0x3)# 利用可能な16ビットUUID(全てのUUIDをAD Dataに含める場合)
_ADV_TYPE_UUID32_COMPLETE = const(0x5)
_ADV_TYPE_UUID128_COMPLETE = const(0x7)
_ADV_TYPE_UUID16_MORE = const(0x2)    # 利用可能な16ビットUUID(一部のUUIDのみAD Dataに含める場合)
_ADV_TYPE_UUID32_MORE = const(0x4)
_ADV_TYPE_UUID128_MORE = const(0x6)
_ADV_TYPE_APPEARANCE = const(0x19)    # デバイスの機能種別名
_ADV_TYPE_SPECIFIC_DATA = const(0xFF)    # 任意の送信データ(ベンダー固有のデータ)を送れる
_ADV_DATA_COMPANY_ID = const(0xFFFF)    # ベンダーのID

# gap_advertise(adv_data = ...)に渡されるメッセージパケットを生成します。
# limited_disc : False=LE 一般検出可能モード　True=LE 限定検出可能モード
# br_edr : False=BR/EDRはサポートされていません　True=0x18?
# name : デバイス名で任意につけてOK、iphone等のアプリ画面上にこの装置名が表示されます
# services : サービスのUUID
# appearance : https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Characteristics/org.bluetooth.characteristic.gap.appearance.xml
def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None, appearance=0, free=None):
    payload = bytearray()

    # アドバータイジングパケットの１データをパックします。
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
        self._payload = advertising_payload(name="swaggy2", services=[_UART_UUID])
        self._advertise()

    # 接続状態の取得
    def is_connected(self):
        return len(self._connections) > 0

    # データ送信
    def send(self, data):
        if self.is_connected():
            for handle in self._connections:
                self._ble.gatts_notify(handle, self._handle_rx, data)
                self._ble.gatts_notify(handle, self._handle_tx, data)

    # イベントコールバック
    def _irq(self, event, data):
        # セントラルに接続
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
            print("Connection", conn_handle)

        # セントラルから切断
        elif event == _IRQ_CENTRAL_DISCONNECT:
            print("Disconnected")
            conn_handle, _, _ = data
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)
                
            #self._advertise()
            print("Disconnected", conn_handle)

        # セントラルからの書き込み
        elif event == _IRQ_GATTS_WRITE:
            print('Read')
            conn_handle, value_handle = data
            # データを読み込む
            value = self._ble.gatts_read(value_handle)
            if value_handle == self._handle_rx:
                print("Rx", value)

    # Advertise開始
    def _advertise(self):
        self._ble.gap_advertise(500000, adv_data=self._payload)
        #self._ble.gap_advertise(500, "MindRender")
        print("Advertise")

ble = BLEPeripheral()
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
    
    # uncomment if you want to see the accel data
    # print(accs)

    ble.send(str(acc))
    print(acc)
    
    #display an arrow on hub display with increasing brightness
    for i in range(11):
        hub.light_matrix.show_image('ARROW_N', brightness=i*10)
        utime.sleep(.1)
