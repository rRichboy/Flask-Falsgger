from datetime import datetime

from psycopg2.extras import RealDictCursor

from db import get_db_connection


# sensors
def get_all_sensors():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM sensors")
    sensors = cursor.fetchall()
    cursor.close()
    conn.close()
    return sensors


def get_sensor(sensor_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM sensors WHERE id = %s", (sensor_id,))
    sensor = cursor.fetchone()
    cursor.close()
    conn.close()
    return sensor


def create_sensor(sensor_name, measurements):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("INSERT INTO sensors (name) VALUES (%s) RETURNING id", (sensor_name,))
    sensor_id = cursor.fetchone()['id']
    for measurement in measurements:
        cursor.execute("""
            INSERT INTO sensors_measurements (sensor_id, type_id, measurment_formula)
            VALUES (%s, %s, %s)
        """, (sensor_id, measurement['type_id'], measurement.get('type_formula')))
    conn.commit()
    cursor.close()
    conn.close()
    return sensor_id


def update_sensor(sensor_id, sensor_name=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if sensor_name is not None:
        cursor.execute("UPDATE sensors SET name = %s WHERE id = %s", (sensor_name, sensor_id))
        if cursor.rowcount == 0:
            conn.rollback()
            cursor.close()
            conn.close()
            return None
    else:
        cursor.execute("UPDATE sensors SET id = %s WHERE id = %s", (sensor_id, sensor_id))
    conn.commit()
    cursor.close()
    conn.close()
    return get_sensor(sensor_id)


def get_sensor_types(sensor_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""SELECT mt.id as type_id, mt.name as type_name, mt.units as type_units, sm.measurment_formula as type_formula
         FROM sensors_measurements sm
         JOIN measurements_type mt ON sm.type_id = mt.id
         WHERE sm.sensor_id = %s
    """, (sensor_id,))
    sensor_types = cursor.fetchall()
    cursor.close()
    conn.close()
    return sensor_types


def delete_sensor(sensor_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM sensors_measurements WHERE sensor_id = %s", (sensor_id,))
        cursor.execute("DELETE FROM sensors WHERE id = %s", (sensor_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


# measurment types
def get_all_measurement_types():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM measurements_type")
    measurement_types = cursor.fetchall()
    cursor.close()
    conn.close()
    return measurement_types


def create_measurement_type(name, units):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        INSERT INTO measurements_type (name, units)
        VALUES (%s, %s)
        RETURNING id
    """, (name, units))
    measurement_type_id = cursor.fetchone()['id']
    conn.commit()
    cursor.close()
    conn.close()
    return measurement_type_id


def update_measurement_type(type_id, name, units):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE measurements_type SET name = %s, units = %s WHERE id = %s", (name, units, type_id))
    conn.commit()
    cursor.close()
    conn.close()


def delete_measurement_type(type_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM measurements_type WHERE id = %s", (type_id,))
    conn.commit()
    cursor.close()
    conn.close()


# meteostations
def get_all_meteostations():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM meteostations")
    meteostations = cursor.fetchall()
    cursor.close()
    conn.close()
    return meteostations


def get_meteostation(station_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM meteostations WHERE id = %s", (station_id,))
    meteostation = cursor.fetchone()
    cursor.close()
    conn.close()
    return meteostation


def create_meteostation(name, longitude, latitude):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        INSERT INTO meteostations (name, longitude, latitude)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (name, longitude, latitude))
    station_id = cursor.fetchone()['id']
    conn.commit()
    cursor.close()
    conn.close()
    return station_id


def update_meteostation(station_id, name, longitude, latitude):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE meteostations
        SET name = %s, longitude = %s, latitude = %s
        WHERE id = %s
    """, (name, longitude, latitude, station_id))
    conn.commit()
    cursor.close()
    conn.close()


def delete_meteostation(station_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM meteostations_sensors WHERE station_id = %s", (station_id,))
        cursor.execute("DELETE FROM meteostations WHERE id = %s", (station_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def get_sensors_by_station_id(station_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT DISTINCT s.id, s.name
        FROM sensors s
        JOIN meteostations_sensors ms ON s.id = ms.sensor_id
        WHERE ms.station_id = %s
        ORDER BY s.id
    """, (station_id,))
    sensors = cursor.fetchall()
    cursor.close()
    conn.close()
    return sensors


# sensors measurements

def add_sensor_measurements(sensor_id, sensors_measurements):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        for measurement in sensors_measurements:
            cursor.execute("""
                INSERT INTO sensors_measurements (sensor_id, type_id, measurment_formula)
                VALUES (%s, %s, %s)
                """, (sensor_id, measurement['type_id'], measurement.get('type_formula', '')))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def delete_sensor_measurements(sensor_id, measurements_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM sensors_measurements
            WHERE sensor_id = %s AND type_id = ANY(%s)
            """, (sensor_id, measurements_type))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


# meteostation sensors

def add_meteostation_sensors(meteostations_sensors):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        for ms in meteostations_sensors:
            cursor.execute("""
                INSERT INTO meteostations_sensors (station_id, sensor_id, added_ts)
                VALUES (%s, %s, %s)
                """, (
                ms['station_id'], ms['sensor_id'], ms.get('added_ts', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def remove_meteostation_sensor(sensor_inventory_number, removed_ts=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if not removed_ts:
            removed_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            UPDATE meteostations_sensors
            SET removed_ts = %s
            WHERE inventory_number = %s
            """, (removed_ts, sensor_inventory_number))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def get_all_meteostation_sensors():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM meteostations_sensors")
    sensors = cursor.fetchall()
    cursor.close()
    conn.close()
    return sensors


# measurment

def add_measurements(measurements):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        for measurement in measurements:
            cursor.execute("""
                    INSERT INTO measurements (sensor_inventory_number, value, ts, type)
                    VALUES (%s, %s, %s, %s)
                    """, (
                measurement['sensor_inventory_number'], measurement['value'], measurement['ts'], measurement['type']))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def get_all_measurements():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM measurements")
    measurements = cursor.fetchall()
    cursor.close()
    conn.close()
    return measurements


def get_measurements_with_conditions(meteostation=None, sensors=None):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    query = "SELECT m.* FROM measurements m"
    conditions = []
    params = []

    if meteostation:
        query += " JOIN meteostations_sensors ms ON m.sensor_inventory_number = ms.inventory_number"
        conditions.append("ms.station_id = %s")
        params.append(meteostation)

    if sensors:
        conditions.append("m.sensor_inventory_number = ANY(%s)")
        params.append(sensors)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, params)
    measurements = cursor.fetchall()
    cursor.close()
    conn.close()
    return measurements
