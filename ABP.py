import time
import socket
import binascii
import struct
import pycom

from CayenneLPP import CayenneLPP
from network import LoRa
from pysense import Pysense
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2, ALTITUDE, PRESSURE

py = Pysense()
si = SI7006A20(py)
lt = LTR329ALS01(py)
li = LIS2HH12(py)

# Disable heartbeat LED
pycom.heartbeat(False)

# Initialize LoRa in LORAWAN mode.
# Europe = LoRa.EU868
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

# create an ABP authentication params
dev_addr = struct.unpack(">l", binascii.unhexlify('2601124B'))[0]
nwk_swkey = binascii.unhexlify('BB6199E4359881D25E05645707108364')
app_swkey = binascii.unhexlify('9DF848B7CDFABE4A95CC2AA044647C16')

# join a network using ABP (Activation By Personalization)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

pycom.rgbled(0x00FF00)
print('Joined LoRa Network')
time.sleep(1)

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

while True:
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
    time.sleep(30)
    pycom.heartbeat(True)