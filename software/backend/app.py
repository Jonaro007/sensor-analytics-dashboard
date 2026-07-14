# -------------------------
# Server for storing data from the ESP32 in the database.
# -------------------------

from flask import Flask, request, jsonify
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_NAME = BASE_DIR / "sensor_data.db"

app = Flask(__name__)



def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # ---------------- GPS ----------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS gps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tripID INTEGER,
        timestamp TEXT,
        lat REAL,
        long REAL,
        speed REAL,
        satellites INTEGER,
        hoehe REAL,
        genauigkeit REAL
    )
    """)

    # ---------------- MPU ----------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS mpu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tripID INTEGER,
        timestamp TEXT,
        gyro_x REAL,
        gyro_y REAL,
        gyro_z REAL,
        accel_x REAL,
        accel_y REAL,
        accel_z REAL
    )
    """)

    # ---------------- BME ----------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS bme (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tripID INTEGER,
        timestamp TEXT,
        pressure REAL,
        temperature REAL,
        humidity REAL
    )
    """)

    conn.commit()
    conn.close()

init_db()



def sort_data(data):
    for item in data["data"]:

        if item["type"] == "gps":
            gps = item["data"]
            tripID = item.get("trip")

            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()

            c.execute("""
            INSERT INTO gps (tripID,timestamp, lat, long, speed, satellites, hoehe, genauigkeit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tripID,
                gps["uhrzeit"],
                gps["latitude"],
                gps["longitude"],
                gps["geschwindigkeit"],
                gps["satelitenanzahl"],
                gps["hoehe"],
                gps["genauigkeit"]
            ))

            conn.commit()
            conn.close()

        elif item["type"] == "mpu":

            mpu_timestamp = item.get("timestamp")
            mpu_list = item.get("data", [])
            mpu_tripID = item.get("trip")
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()

            for mpu_data in mpu_list:

                mpu = mpu_data

                c.execute("""
                INSERT INTO mpu (tripID, timestamp, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    mpu_tripID,
                    mpu_timestamp,
                    mpu.get("gx"),
                    mpu.get("gy"),
                    mpu.get("gz"),
                    mpu.get("ax"),
                    mpu.get("ay"),
                    mpu.get("az")
                ))

            conn.commit()
            conn.close()
            
        elif item["type"] == "bme":
            bme = item["data"]
            bme_tripID = item.get("trip")
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()

            c.execute("""
            INSERT INTO bme (tripID, timestamp, pressure, temperature, humidity)
            VALUES (?, ?, ?, ?, ?)
            """, (
                bme_tripID,
                item["timestamp"],
                bme["pressure"],
                bme["temperature"],
                bme["humidity"]
            ))

            conn.commit()
            conn.close()


@app.route("/data", methods=["POST"])
def data():
    content = request.json
    sort_data(content)
    return jsonify({"status": "ok"}), 200


@app.route("/data", methods=["GET"])
def data_get():
    return "Use POST", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)