from machine import UART, Pin
import time

geschwindigkeit = None
gps = UART(2, 9600)
gps.init(9600, bits=8, parity=None, stop=1, tx=Pin(17), rx=Pin(16))

def gps_ok(parts):
    if len(parts) < 8:
        return False

    fix = parts[6]

    if fix != "1":
        return False

    return True


def get_uhrzeit(uhrzeit):
    if len(uhrzeit) < 6:
        return "00:00:00"

    stunde = (int(uhrzeit[0:2]) + 2) % 24
    minute = uhrzeit[2:4]
    sekunde = uhrzeit[4:6]
    return f"{stunde:02d}:{minute}:{sekunde}"



def get_gps_data():
    global geschwindigkeit

    while gps.any():

        line = gps.readline()
        if line is None:
            return None

        try:
            text = line.decode().strip()
        except:
            return None

        if text.startswith("$GPGGA"):
            parts = text.split(",")

            if not gps_ok(parts):
                return None

            gps_zeit = parts[1]
            lat_raw = parts[2]
            lat_dir = parts[3]
            lon_raw = parts[4]
            lon_dir = parts[5]
            sat = parts[7]
            hdop = parts[8]
            hoehe = parts[9]

            if lat_raw == "" or lon_raw == "":
                return None
            if len(lat_raw) < 6 or len(lon_raw) < 7:
                return None

            try:
                lat_grad = int(lat_raw[0:2])
                lat_minuten = float(lat_raw[2:])

                lon_grad = int(lon_raw[0:3])
                lon_minuten = float(lon_raw[3:])
            except:
                return None

            try:
                lat_grad = int(lat_raw[0:2])
                lat_minuten = float(lat_raw[2:])

                lon_grad = int(lon_raw[0:3])
                lon_minuten = float(lon_raw[3:])
            except:
                return None

            lat_grad = int(lat_raw[0:2])
            lat_minuten = float(lat_raw[2:])
            lat_dezimal = lat_grad + (lat_minuten / 60)
            if lat_dir == "S":
                lat_dezimal = -lat_dezimal

            lon_grad = int(lon_raw[0:3])
            lon_minuten = float(lon_raw[3:])
            lon_dezimal = lon_grad + (lon_minuten / 60)
            if lon_dir == "W":
                lon_dezimal = -lon_dezimal

            return {
                "uhrzeit": get_uhrzeit(gps_zeit),
                "latitude": lat_dezimal,
                "longitude": lon_dezimal,
                "satelitenanzahl": sat,
                "hoehe": hoehe,
                "genauigkeit": float(hdop) * 2.5 if hdop else None,
                "geschwindigkeit": geschwindigkeit
            }

        elif text.startswith("$GPRMC"):
            parts = text.split(",")
            if len(parts) < 8:
                return None
            if parts[7] != "":
                try:
                    geschwindigkeit = float(parts[7]) * 1.852
                except:
                    pass

    return None

