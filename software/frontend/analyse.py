# -------------------------
# Extract all data from the database and prepare it for the dashboard
# -------------------------
from datetime import datetime, timedelta
import math
import sqlite3

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_NAME = BASE_DIR / "sensor_data.db"


def get_all_data(tripid):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT timestamp, lat, long, speed, satellites, hoehe, genauigkeit
        FROM gps
        WHERE tripID = ?
        ORDER BY timestamp
    """, (tripid,))
    gps = [dict(row) for row in c.fetchall()]

    c.execute("""
        SELECT timestamp, temperature, humidity, pressure
        FROM bme
        WHERE tripID = ?
        ORDER BY timestamp
    """, (tripid,))
    bme = [dict(row) for row in c.fetchall()]

    c.execute("""
        SELECT timestamp, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z
        FROM mpu
        WHERE tripID = ?
        ORDER BY timestamp
    """, (tripid,))
    mpu = [dict(row) for row in c.fetchall()]

    conn.close()

    return {
        "gps": gps,
        "bme": bme,
        "mpu": mpu
    }

def get_short_term_data(tripid, start_minute=0, duration_minutes=1):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        tripid = int(tripid)
        start_minute = int(start_minute)
        duration_minutes = int(duration_minutes)

        c.execute("""
            SELECT timestamp
            FROM mpu
            WHERE tripID = ?
            ORDER BY id ASC
            LIMIT 1
        """, (tripid,))

        row = c.fetchone()

        if row is None:
            return {"gps": [], "bme": [], "mpu": []}

        start_time = row["timestamp"]
        start_dt = datetime.strptime(start_time, "%H:%M:%S")

        from_time = (start_dt + timedelta(minutes=start_minute)).strftime("%H:%M:%S")
        to_time = (start_dt + timedelta(minutes=start_minute + duration_minutes)).strftime("%H:%M:%S")

        def fetch(table, columns):
            c.execute(f"""
                SELECT {columns}
                FROM {table}
                WHERE tripID = ?
                AND timestamp >= ?
                AND timestamp < ?
                ORDER BY id ASC
            """, (tripid, from_time, to_time))

            return [dict(row) for row in c.fetchall()]

        gps = fetch(
            "gps",
            "timestamp, lat, long, speed, satellites, hoehe, genauigkeit"
        )

        bme = fetch(
            "bme",
            "timestamp, temperature, humidity, pressure"
        )

        mpu = fetch(
            "mpu",
            "timestamp, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z"
        )

        return {
            "gps": gps,
            "bme": bme,
            "mpu": mpu,
            "from_time": from_time,
            "to_time": to_time
        }

    except Exception as e:
        print("get_short_term_data error:", e)
        return {"gps": [], "bme": [], "mpu": []}

    finally:
        conn.close()


# -------------------------
# DISTANCE
# -------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def total_distance(points):
    dist = 0
    for i in range(1, len(points)):
        lat1, lon1 = points[i - 1]
        lat2, lon2 = points[i]
        dist += haversine(lat1, lon1, lat2, lon2)
    return dist


# -------------------------
# TIME RANGE
# -------------------------
def get_global_time_range(gps, bme, mpu):
    times = (
        [x["timestamp"] for x in gps if x.get("timestamp")] +
        [x["timestamp"] for x in bme if x.get("timestamp")] +
        [x["timestamp"] for x in mpu if x.get("timestamp")]
    )

    if not times:
        return None, None, None

    start = min(times)
    end = max(times)

    fmt = "%H:%M:%S"

    try:
        start_dt = datetime.strptime(start, fmt)
        end_dt = datetime.strptime(end, fmt)
        duration = end_dt - start_dt
    except:
        duration = None

    return start, end, duration


# -------------------------
# SHORT TERM ANALYSIS
# -------------------------
def analyse(term, minute, tripid):
    gps_func = "Ok"
    if term == "short":   
        print("test")
        data = get_short_term_data(tripid, start_minute=minute, duration_minutes=1)
        print("test1")
    else:
        data = get_all_data(tripid)
    gps = data["gps"]
    bme = data["bme"]
    mpu = data["mpu"]
    print(f"GPS: {len(gps)} points, BME: {len(bme)} points, MPU: {len(mpu)} points")
    

    # ---------------- GPS ----------------
    speeds = [x["speed"] for x in gps if x.get("speed") is not None]
    speed_raw = []
    timestamp_raw = []
    gps_raw_data = []
    mpu_raw_data = []
    bme_raw_data = []

    for d in gps:
        speed = d.get("speed")
        timestamp = d.get("timestamp")
        lat = d.get("lat")
        long = d.get("long")
        satellites_raw = d.get("satellites")
        hoehe = d.get("hoehe")
        genauigkeit = d.get("genauigkeit")
        

        # Für den bisherigen Geschwindigkeitsgraphen
        if speed is not None and timestamp is not None:
            timestamp_raw.append(timestamp)
            speed_raw.append(float(speed))

        gps_raw_data.append({
            "timestamp": timestamp,
            "lat": float(lat) if lat is not None else None,
            "long": float(long) if long is not None else None,
            "speed": float(speed) if speed is not None else None,
            "satellites": (
                int(float(satellites_raw))
                if satellites_raw is not None
                else None
            ),
            "accuracy": (
                float(genauigkeit)
                if genauigkeit is not None
                else None
            ),
            "height": (
                float(hoehe)
                if hoehe is not None
                else None
            )
        })

    if len(gps) == 0:
        gps_func = "Error"
    else:
        avg_speed = sum(speeds) / len(speeds)
        max_speed = max(speeds)
        min_speed = min(speeds)

        variance = sum((x - avg_speed) ** 2 for x in speeds) / len(speeds)
        std_dev = math.sqrt(variance)

        if std_dev > 10:
            variability = "high"
        elif std_dev > 2:
            variability = "moderate"
        else:
            variability = "low"

        grenze = 2.0

        time_standing = sum(1 for s in speeds if s < grenze)
        time_moving = len(speeds) - time_standing

        standing_percent = time_standing / len(speeds) * 100
        moving_percent = time_moving / len(speeds) * 100

        distance_points = [
            (x["lat"], x["long"])
            for x in gps
            if x.get("lat") is not None and x.get("long") is not None
        ]

        total_dist = total_distance(distance_points)

        valid_acc = [x["genauigkeit"] for x in gps if x.get("genauigkeit") is not None]
        gps_accuracy = sum(valid_acc) / len(valid_acc) if valid_acc else None

        satellites = []

        for row in gps:
            value = row.get("satellites")

            if value in (None, "", 0, "0"):
                continue

            try:
                satellites.append(int(float(value)))
            except (TypeError, ValueError):
                print("Ungültiger Satellitenwert:", repr(value))

        avg_satellites = (
            sum(satellites) / len(satellites)
            if satellites
            else 0
        )
    height = [x["hoehe"] for x in gps if x.get("hoehe") is not None]
    avg_height = sum(height) / len(height)


    # ---------------- MPU ----------------

    break_count = 0
    accel_count = 0
    left_turn = 0
    right_turn = 0

    max_impact = 0
    vibration_sum = 0
    strong_impact = 0

    last_events = []
    impact_over_time = []

    accel_active = False
    break_active = False
    impact_active = False
    left_turn_active = False
    right_turn_active = False

    for d in mpu:
        ax = float(d.get("accel_x", 0))
        ay = float(d.get("accel_y", 0))
        az = float(d.get("accel_z", 0))
        gz = float(d.get("gyro_z", 0))

        mpu_raw_data.append ({
            "timestamp": d.get("timestamp"),
            "ax": ax,
            "ay": ay,
            "az": az,
            "gz": gz
        })

        timestamp = d.get("timestamp", "")

        # Hard braking
        if ax < -3000 and not break_active:
            break_count += 1
            break_active = True

            last_events.append({
                "type": "Hard braking",
                "timestamp": timestamp
            })

        elif ax > -2000:
            break_active = False

        # Strong acceleration
        if ax > 3000 and not accel_active:
            accel_count += 1
            accel_active = True

            last_events.append({
                "type": "Strong acceleration",
                "timestamp": timestamp
            })

        elif ax < 2000:
            accel_active = False

        # Left turn
        if gz < -3000 and not right_turn_active:
            right_turn += 1
            right_turn_active = True

            last_events.append({
                "type": "Left turn",
                "timestamp": timestamp
            })

        elif gz > -2000:
            right_turn_active = False

        # Right turn
        if gz > 3000 and not left_turn_active:
            left_turn += 1
            left_turn_active = True

            last_events.append({
                "type": "Right turn",
                "timestamp": timestamp
            })

        elif gz < 2000:
            left_turn_active = False

        # Impact
        magnitude = math.sqrt(ax**2 + ay**2 + az**2)
        impact = abs(magnitude - 16384)

        impact_over_time.append({
            "timestamp": timestamp,
            "impact": impact
        })

        max_impact = max(max_impact, impact)
        vibration_sum += impact

        # Strong impact event
        if impact > 5000 and not impact_active:
            strong_impact += 1
            impact_active = True

            last_events.append({
                "type": "Strong impact",
                "timestamp": timestamp
            })

        elif impact < 3000:
            impact_active = False

    vibration_level = vibration_sum / len(mpu) if mpu else 0

    # ---------------- BME ----------------

    for d in bme:
        temperature = float(d.get("temperature", 0))
        pressure = float(d.get("pressure", 0))
        humidity = float(d.get("humidity", 0))
        

        bme_raw_data.append ({
            "timestamp": d.get("timestamp"),
            "temperature": temperature,
            "pressure": pressure,
            "humidity": humidity,
        })


    temp = [x["temperature"] for x in bme if x.get("temperature") is not None]
    press = [x["pressure"] for x in bme if x.get("pressure") is not None]
    humidity = [x["humidity"] for x in bme if x.get("humidity") is not None]

    avg_temp = sum(temp) / len(temp)
    max_temp = max(temp)
    min_temp = min(temp)

    avg_press = sum(press) / len(press)
    max_press = max(press)
    min_press = min(press)

    avg_humidity = sum(humidity) / len(humidity)
    max_humidity = max(humidity)
    min_humidity = min(humidity)
    
    
    
    # ---------------- TIME ----------------
    start, end, duration = get_global_time_range(gps, bme, mpu)

    # ---------------- RETURN ----------------
    print(duration, "\n\n\n")
    return {
        "time": {
            "start": start,
            "end": end,
            "duration": str(duration)
        },

        "gps": {
            "gps_func": gps_func,
            "avg_speed": avg_speed,
            "max_speed": max_speed,
            "min_speed": min_speed,
            "speed_variance": variance,
            "speed_std_dev": std_dev,
            "variability": variability,
            "time_standing": standing_percent,
            "time_moving": moving_percent,
            "distance_total": total_dist,
            "gps_accuracy_avg": gps_accuracy,
            "avg_satellites": avg_satellites,
            "avg_height": avg_height,
            "points": [
                {"lat": x["lat"], "long": x["long"]}
                for x in gps
                if x.get("lat") is not None and x.get("long") is not None
            ]
        },

        "mpu": {
            "hard_brake_count": break_count,
            "hard_accel_count": accel_count,
            "turn_left_count": left_turn,
            "turn_right_count": right_turn,
            "max_impact": max_impact,
            "vibration_level": vibration_level,
            "strong_impact": strong_impact,
            "last_events" : last_events,
            "all_impact_data": impact_over_time
            
        },

        "bme": {
            "avg_temp": avg_temp,
            "avg_press": avg_press,
            "avg_humidity": avg_humidity,
            "max_temp": max_temp,
            "max_press": max_press,
            "max_humidity": max_humidity,
            "min_temp": min_temp,
            "min_press": min_press,
            "min_humidity": min_humidity,
        },

        "raw_data": {
            "speed" : speed_raw,
            "timestamp_gps": timestamp_raw,
            "vib" : impact_over_time
            
        },
        "all_data" : {
            "gps": gps_raw_data,
            "bme" : bme_raw_data,
            "mpu" : mpu_raw_data
        }
    }

# ---------------- Obtain data for specific purposes ----------------


def fahrten():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        c.execute("""
            SELECT tripID, MIN(timestamp) AS start_time
            FROM gps
            GROUP BY tripID
            ORDER BY tripID
        """)

        fahrten_dict = {
            f"Ride {row['tripID']} - {row['start_time']}": row["tripID"]
            for row in c.fetchall()
        }

    except sqlite3.OperationalError:
        fahrten_dict = {}

    conn.close()
    return fahrten_dict


def get_trip_dauer(tripID):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT MIN(timestamp) AS start_time,
               MAX(timestamp) AS end_time
        FROM mpu
        WHERE tripID = ?
    """, (tripID,))

    row = c.fetchone()
    conn.close()

    if row["start_time"] is None:
        return None

    start = datetime.strptime(row["start_time"], "%H:%M:%S")
    ende = datetime.strptime(row["end_time"], "%H:%M:%S")

    dauer = ende - start
    return int(dauer.total_seconds() // 60)


