import pycom
import _thread
from pysense import Pysense
from SI7006A20 import SI7006A20
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE
from LTR329ALS01 import LTR329ALS01
from LIS2HH12 import LIS2HH12
from time import sleep
import time
from network import LoRa
import socket
from CayenneLPP import CayenneLPP
import binascii
import urequests as requests
from machine import Pin

uart1 = UART(1, 115200, bits=8, parity=None, stop=1)
uart1.init(baudrate=115200, bits=8, parity=None, stop=1, timeout_chars=2, pins=("P3", "P4"))
uart1.write("Connected...")



pycom.heartbeat(False)

py = Pysense()         # Connect to the PySense board

si = SI7006A20(py)     # Connect to the temperature sensor
mpa = MPL3115A2(py,mode=ALTITUDE)
mpp = MPL3115A2(py,mode=PRESSURE)
lt = LTR329ALS01(py)
li = LIS2HH12(py)

lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
dev_eui = binascii.unhexlify('70B3D5499925EAA1')
app_eui = binascii.unhexlify('70B3D57ED001D939')
app_key = binascii.unhexlify('4CFC04440591BEC8EFFD9FC4D13B29FE')

print("DevEUI: %s" % (binascii.hexlify(lora.mac())))
print("AppEUI: %s" % (binascii.hexlify(app_eui)))
print("AppKey: %s" % (binascii.hexlify(app_key)))

lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
pycom.rgbled(0x7f7f00)          # yellow
count = 0

while not lora.has_joined():
    sleep(2.5)
    pycom.rgbled(0x7f0000) # red
    sleep(1.0)
    print("[" + str(time.time()) + "] not joined the network yet [count=" + str(count) + "]")
    count = count + 1

pycom.rgbled(0x001400)
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

DEVICE_SECRET_KEY = 'd_sk_WWzctttAsj8PUcjCB0bLoY2y'
url = "https://api.wia.io/v1/events"
headers = { "Authorization": "Bearer " + DEVICE_SECRET_KEY, "Content-Type": "application/json" }

def post_event(name, data):
    try:
        json_data = { "name": name, "data": data }
        print(str(json_data))
        if json_data is not None:
            req = requests.post(url=url, headers=headers, json=json_data)
            return req.json()
        else:
            pass
    except:
        pass

while True:
    pycom.rgbled(0x0000FF)         # Flash the LED blue
    temp = si.temperature()        # Get the temperature
    pybytes.send_signal(0, si.temperature())   # Send the temperature using signal 0
    pycom.rgbled(0x000000)         # Turn off the LED



    receiving = urat1.readall().decode('uft-8')
    if data == b'send':
            send_lora("data")
            pycom.rgbled(0x00FF00) # set LED to GREEN if data is b'send'
    time.sleep(1)

    pybytes.send_signal(7,receiving)


    pycom.rgbled(0x0000FF)         # Flash the LED blue
    humidity = si.humidity()        # Get the humidity
    pybytes.send_signal(1, si.humidity())   # Send the Humidity using signal 1
    pycom.rgbled(0x000000)         # Turn off the LED

    pycom.rgbled(0x0000FF)         # Flash the LED blue
    mpp = MPL3115A2(py,mode=PRESSURE)
    pressure = mpp.pressure()        # Get the pressure
    pybytes.send_signal(4, mpp.pressure()/100)   # Send the pressure using signal 4
    pycom.rgbled(0x000000)         # Turn off the LED

    pycom.rgbled(0x0000FF)         # Flash the LED blue
    mpa = MPL3115A2(py,mode=ALTITUDE)
    altitude = mpa.altitude()        # Get the altitude
    pybytes.send_signal(5, mpa.altitude()/100)   # Send the altitude using signal 5
    pycom.rgbled(0x000000)         # Turn off the LED

    light = lt.light()        # Get the Light
    pybytes.send_signal(2, lt.light())   # Send the light using signal 2
    pycom.rgbled(0x000000)         # Turn off the LED

    Acceleration = li.acceleration()        # Get the acceleration
    pybytes.send_signal(3, li.acceleration())   # Send the acceleration using signal 3
    pycom.rgbled(0x000000)         # Turn off the LED

    battery = py.read_battery_voltage()        # Get the battery voltage
    pybytes.send_signal(6, py.read_battery_voltage())   # Send the battery using signal 6
    pycom.rgbled(0x000000)         # Turn off the LED

    post_event("temperature", si.temperature())
    mpp = MPL3115A2(py,mode=PRESSURE)
    post_event("pressure", mpp.pressure()/100)
    mpa = MPL3115A2(py,mode=ALTITUDE)
    post_event("altitude", mpa.altitude()/100)
    post_event("humidity", si.humidity())
    post_event("light", lt.light())
    pycom.rgbled(0x000000)

    s.setblocking(True)
    pycom.rgbled(0x000014)
    lpp = CayenneLPP()

    print('\n\n** 3-Axis Accelerometer (LIS2HH12)')
    print('Acceleration', li.acceleration())
    print('Roll', li.roll())
    print('Pitch', li.pitch())
    lpp.add_accelerometer(1, li.acceleration()[0], li.acceleration()[1], li.acceleration()[2])
    lpp.add_gryrometer(1, li.roll(), li.pitch(), 0)

    print('\n\n** Digital Ambient Light Sensor (LTR-329ALS-01)')
    print('Light', lt.light())
    lpp.add_luminosity(1, lt.light()[0])
    lpp.add_luminosity(2, lt.light()[1])

    print('\n\n** Humidity and Temperature Sensor (SI7006A20)')
    print('Humidity', si.humidity())
    print('Temperature', si.temperature())
    lpp.add_relative_humidity(1, si.humidity())
    lpp.add_temperature(1, si.temperature())

    mpPress = MPL3115A2(py,mode=PRESSURE)
    print('\n\n** Barometric Pressure Sensor with Altimeter (MPL3115A2)')
    print('Pressure (hPa)', mpPress.pressure()/100)
    lpp.add_barometric_pressure(1, mpPress.pressure()/100)

    mpAlt = MPL3115A2(py,mode=ALTITUDE)
    print('Altitude', mpAlt.altitude())
    print('Temperature', mpAlt.temperature())
    lpp.add_gps(1, 0, 0, mpAlt.altitude())
    lpp.add_temperature(2, mpAlt.temperature())

    print('Sending data (uplink)...')
    s.send(bytes(lpp.get_buffer()))
    s.setblocking(False)
    data = s.recv(64)
    print('Received data (downlink)', data)
    pycom.rgbled(0x001400)

    sleep(3600)                       # Sleep for 1hr
