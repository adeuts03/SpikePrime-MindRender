# BLE
This method is pretty straightforward, you just build out your LEGO device and then run some code. 

File descriptions:
- MR_car.py: SPIKE code that turns the hub into a gyroscope based steering wheel/accelerator and sends data to MR
- MR_car_spike3.py: MR_car.py but we started porting it to Atlantis
- MR_golf.py: SPIKE code that turns the hub into a golf club and sends data to MR
- SpikeSendBLE.py: SPIKE code that turns the hub into a steering wheel/accelerator and sends data to MR
- SpikeSendReceiveBLE.py: SpikeSendBLE.py but now it can receive data
- SpikeSendReceiveBLE_3.py: SpikeSendBLE.py but ported to Atlantis, as of right now BLE on there is weird