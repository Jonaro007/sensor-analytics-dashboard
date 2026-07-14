from machine import I2C
import time

class MPU6050:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr

        time.sleep(0.1)

        # Wake up MPU6050
        try:
            self.i2c.writeto_mem(self.addr, 0x6B, b'\x00')
        except:
            raise Exception("MPU6050 nicht gefunden (Adresse falsch oder Verkabelung)")

    def read_raw(self):
        return self.i2c.readfrom_mem(self.addr, 0x3B, 14)

    def get_values(self):
        data = self.read_raw()

        def to_int(h, l):
            val = (h << 8) | l
            if val > 32767:
                val -= 65536
            return val

        accel_x = to_int(data[0], data[1])
        accel_y = to_int(data[2], data[3])
        accel_z = to_int(data[4], data[5])

        temp = to_int(data[6], data[7]) / 340.0 + 36.53

        gyro_x = to_int(data[8], data[9])
        gyro_y = to_int(data[10], data[11])
        gyro_z = to_int(data[12], data[13])

        return {
            "AcX": accel_x,
            "AcY": accel_y,
            "AcZ": accel_z,
            "Temp": temp,
            "GyX": gyro_x,
            "GyY": gyro_y,
            "GyZ": gyro_z
        }