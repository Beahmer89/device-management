import duckdb
import uuid

con = duckdb.connect(database="test_db.duckdb")


def create_device(request_data):
    device_uuid = str(uuid.uuid4())
    device_type = request_data["type"]
    device_state = request_data["state"]
    result = con.execute(
        "INSERT INTO devices (uuid, type, state, hub_uuid) VALUES (?, ?, ?, ?) RETURNING (uuid);",
        (device_uuid, device_type, device_state, None),
    ).fetchone()
    return str(result[0])


def get_device_by_uuid(device_uuid):
    result = con.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()
    return result


def update_device_by_uuid(device_uuid, request_data):
    device_state = request_data["state"]
    result = con.execute(
        "UPDATE devices SET state = ? WHERE uuid = ? RETURNING state",
        (
            device_state,
            device_uuid,
        ),
    ).fetchone()
    return result


def delete_device_by_uuid(device_uuid):
    con.execute("DELETE FROM devices WHERE uuid = ?", (device_uuid,))


def get_all_devices(limit, offset):
    result = con.execute(
        "SELECT * FROM devices LIMIT ? OFFSET ?",
        (
            limit,
            offset,
        ),
    ).fetchall()
    return result
