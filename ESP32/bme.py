from machine import Pin, I2C
import time
import bme280


i2c = I2C(0, scl=Pin(22), sda=Pin(21))


def check_bme():
    devices = i2c.scan()
    if 118 in devices:
        
        return "BME280 ready"
    else:
        return "BME280 not ready"

sensor = bme280.BME280(i2c=i2c)

def read_bme280():
    temp, press, hum = sensor.read_compensated_data()

    temperature = temp / 100
    pressure = press / 25600
    humidity = hum / 1024

    return {
        "temperature": temperature,
        "pressure": pressure,
        "humidity": humidity
    }

