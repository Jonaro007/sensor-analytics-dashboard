import time
import _thread
import os
import network
import urequests as requests
import ujson
import gc

from dotenv import load_dotenv
import os

load_dotenv()

SERVER_URL = "http://172.20.10.4:5000/data"
QUEUE_FILE = "data_queue1.json"
TMP_FILE = "data_queue_tmp.json"
TRIP_FILE = "tripnr.txt"

SSID = os.getenv('SSID')
PASSWORD = os.getenv('PASSWORD')

import bme as bme_sensor
import mpu as mpu_sensor
import gps as gps_sensor

wifi = network.WLAN(network.STA_IF)
wifi.active(True)

last_wifi_attempt = 0
sending_queue = []
lock = _thread.allocate_lock()

max_queue_size = 100
MAX_MPU_SAMPLES = 40
BATCH_SIZE = 20
SEND_INTERVAL = 1000

last_send_time = time.ticks_ms()


def get_timestamp():
    t = time.localtime()
    return "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])


def get_trip_id():
    if TRIP_FILE not in os.listdir():
        with open(TRIP_FILE, "w") as f:
            f.write("2")
        return 1

    with open(TRIP_FILE, "r") as f:
        trip_id = int(f.read().strip())

    with open(TRIP_FILE, "w") as f:
        f.write(str(trip_id + 1))

    return trip_id


tripID = get_trip_id()


def wifi_connect():
    global last_wifi_attempt

    if wifi.isconnected():
        return

    now = time.ticks_ms()
    if time.ticks_diff(now, last_wifi_attempt) < 10000:
        return

    last_wifi_attempt = now
    print("Connecting WiFi...")

    try:
        wifi.disconnect()
    except:
        pass

    wifi.connect(SSID, PASSWORD)

    timeout = 8
    while not wifi.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1

    if wifi.isconnected():
        print("WiFi connected")
    else:
        print("WiFi failed")


def send_to_server(packets):
    try:
        payload = ujson.dumps({
            "device": "esp32",
            "data": packets
        })

        r = requests.post(
            SERVER_URL,
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        ok = r.status_code == 200
        r.close()

        del payload
        gc.collect()
        return ok

    except Exception as e:
        print("Send failed:", e)
        gc.collect()
        return False


def save_queue_to_file():
    global sending_queue

    with lock:
        if len(sending_queue) == 0:
            return

        data_to_save = sending_queue[:]
        sending_queue.clear()

    try:
        with open(QUEUE_FILE, "a") as f:
            for packet in data_to_save:
                f.write(ujson.dumps(packet) + "\n")

        print("Saved offline:", len(data_to_save))

    except Exception as e:
        print("File save failed:", e)

    del data_to_save
    gc.collect()


def send_file_batch():
    if QUEUE_FILE not in os.listdir():
        return False

    packets = []
    sent_lines = 0

    try:
        with open(QUEUE_FILE, "r") as old:
            for line in old:
                if len(packets) < BATCH_SIZE:
                    try:
                        packets.append(ujson.loads(line))
                        sent_lines += 1
                    except:
                        sent_lines += 1
                else:
                    break

        if len(packets) == 0:
            os.remove(QUEUE_FILE)
            return False

        ok = send_to_server(packets)

        if not ok:
            del packets
            gc.collect()
            return False

        skipped = 0

        with open(QUEUE_FILE, "r") as old:
            with open(TMP_FILE, "w") as new:
                for line in old:
                    if skipped < sent_lines:
                        skipped += 1
                    else:
                        new.write(line)

        os.remove(QUEUE_FILE)
        os.rename(TMP_FILE, QUEUE_FILE)

        try:
            if os.stat(QUEUE_FILE)[6] == 0:
                os.remove(QUEUE_FILE)
        except:
            pass

        print("Sent from file:", len(packets))

        del packets
        gc.collect()
        return True

    except Exception as e:
        print("File send failed:", e)

        try:
            if TMP_FILE in os.listdir():
                os.remove(TMP_FILE)
        except:
            pass

        gc.collect()
        return False


def bme_data():
    while True:
        if wifi.isconnected():
            time.sleep(1)
            continue

        data = bme_sensor.read_bme280()

        if data:
            packet = {
                "type": "bme",
                "trip": tripID,
                "timestamp": get_timestamp(),
                "data": data
            }

            with lock:
                if len(sending_queue) < max_queue_size:
                    sending_queue.append(packet)

        time.sleep(30)


def mpu_data():
    collect_data = []
    start = time.ticks_ms()

    while True:
        if wifi.isconnected():
            collect_data = []
            start = time.ticks_ms()
            time.sleep(1)
            continue

        data = mpu_sensor.get_mpu_data()

        if data and len(collect_data) < MAX_MPU_SAMPLES:
            collect_data.append(data)

        if time.ticks_diff(time.ticks_ms(), start) >= 1000:
            packet = {
                "type": "mpu",
                "trip": tripID,
                "timestamp": get_timestamp(),
                "data": collect_data
            }

            with lock:
                if len(sending_queue) < max_queue_size:
                    sending_queue.append(packet)

            collect_data = []
            start = time.ticks_ms()

        time.sleep(0.1)


def gps_data():
    while True:
        if wifi.isconnected():
            time.sleep(1)
            continue

        data = gps_sensor.get_gps_data()

        if data:
            packet = {
                "type": "gps",
                "trip": tripID,
                "timestamp": get_timestamp(),
                "data": data
            }

            with lock:
                if len(sending_queue) < max_queue_size:
                    sending_queue.append(packet)

        time.sleep(1)


_thread.start_new_thread(bme_data, ())
_thread.start_new_thread(mpu_data, ())
_thread.start_new_thread(gps_data, ())

while True:
    wifi_connect()

    if not wifi.isconnected():
        save_queue_to_file()
        time.sleep(0.05)
        continue

    with lock:
        sending_queue.clear()

    send_file_batch()

    gc.collect()
    time.sleep(0.2)
    