from machine import I2C, Pin
import time
from mpu6050 import MPU6050

i2c = I2C(0, scl=Pin(22), sda=Pin(21))


def check_mpu():
    devices = i2c.scan()
    if 104 in devices:
        
        return "MPU6050 ready"
    else:
        return "MPU6050 not ready"
mpu = MPU6050(i2c)



def get_mpu_data():
    data = mpu.get_values()

    return {
        "ax": data["AcX"],
        "ay": data["AcY"],
        "az": data["AcZ"],
        "gx": data["GyX"],
        "gy": data["GyY"],
        "gz": data["GyZ"]
    }
