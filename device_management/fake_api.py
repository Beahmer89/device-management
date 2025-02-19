import duckdb
import uuid

CON = duckdb.connect(database="test_db.duckdb")


def create_device(request_data):
    device_uuid = str(uuid.uuid4())
    device_type = request_data["type"]
    device_state = request_data["state"]
    CON.execute("BEGIN TRANSACTION;")
    result = CON.execute(
        "INSERT INTO devices (uuid, type, state, hub_uuid) VALUES (?, ?, ?, ?) RETURNING (uuid);",
        (device_uuid, device_type, device_state, None),
    ).fetchone()
    CON.execute("COMMIT;")
    return str(result[0])


def get_device_by_uuid(device_uuid):
    result = CON.execute(
        "SELECT * FROM devices WHERE uuid = ?;", (device_uuid,)
    ).fetchone()
    return result


def update_device_by_uuid(device_uuid, request_data):
    device_state = request_data["state"]

    CON.execute("BEGIN TRANSACTION;")
    result = CON.execute(
        "UPDATE devices SET state = ? WHERE uuid = ? RETURNING state;",
        (
            device_state,
            device_uuid,
        ),
    ).fetchone()
    CON.execute("COMMIT;")
    return result


def delete_device_by_uuid(device_uuid):
    CON.execute("DELETE FROM devices WHERE uuid = ?;", (device_uuid,))


def get_all_devices(limit, offset):
    result = CON.execute(
        "SELECT * FROM devices LIMIT ? OFFSET ?;",
        (
            limit,
            offset,
        ),
    ).fetchall()
    return result


def create_hub():
    hub_uuid = str(uuid.uuid4())
    CON.execute("BEGIN TRANSACTION;")
    result = CON.execute(
        "INSERT INTO hubs (uuid) VALUES (?) RETURNING (uuid);",
        (hub_uuid,),
    ).fetchone()
    CON.execute("COMMIT;")
    return str(result[0])


def get_hub_by_uuid(hub_uuid):
    result = CON.execute(
        "SELECT * FROM hubs WHERE uuid = ?;",
        (hub_uuid,),
    ).fetchone()
    return str(result[0]) if result else ""


def get_device_by_hub_and_device_uuid(device_uuid, hub_uuid):
    result = CON.execute(
        "SELECT * FROM devices d WHERE uuid = ? AND hub_uuid = ?;",
        (
            device_uuid,
            hub_uuid,
        ),
    ).fetchone()
    return result if result else ""


def get_devices_by_hub(hub_uuid):
    result = CON.execute(
        "SELECT * FROM devices d INNER JOIN hubs h ON d.hub_uuid = h.uuid WHERE h.uuid = ?;",
        (hub_uuid,),
    ).fetchall()
    return result


def update_device_pairing_by_uuid(device_uuid, request_data):
    hub_uuid = request_data["hub_uuid"]
    CON.execute("BEGIN TRANSACTION;")
    result = CON.execute(
        "UPDATE devices SET hub_uuid = ? WHERE uuid = ? RETURNING hub_uuid;",
        (
            hub_uuid,
            device_uuid,
        ),
    )
    CON.execute("COMMIT;")
    return result


def unpair_device_by_uuid(device_uuid):
    CON.execute("BEGIN TRANSACTION;")
    CON.execute(
        "UPDATE devices SET hub_uuid = NULL WHERE uuid = ?;",
        (device_uuid,),
    )

    CON.execute("COMMIT;")


def create_dwelling():
    dwelling_uuid = str(uuid.uuid4())
    CON.execute("BEGIN TRANSACTION;")
    result = CON.execute(
        "INSERT INTO dwellings (uuid) VALUES (?) RETURNING (uuid);",
        (dwelling_uuid,),
    ).fetchone()
    CON.execute("COMMIT;")
    return str(result[0])


def update_hub_with_dwelling_uuid(hub_uuid, request_data):
    dwelling_uuid = request_data["dwelling_uuid"]
    CON.execute("BEGIN TRANSACTION;")
    result = CON.execute(
        "UPDATE hubs SET dwelling_uuid = ? WHERE uuid = ? RETURNING uuid;",
        (
            dwelling_uuid,
            hub_uuid,
        ),
    ).fetchone()
    CON.execute("COMMIT;")
    return result


def get_dwelling_by_uuid(dwelling_uuid):
    result = CON.execute(
        "SELECT * FROM dwellings WHERE uuid = ?;", (dwelling_uuid,)
    ).fetchone()
    return result


def get_all_dwellings(limit, offset):
    result = CON.execute(
        "SELECT * FROM dwellings LIMIT ? OFFSET ?;",
        (
            limit,
            offset,
        ),
    ).fetchall()
    return result


def get_devices_by_dwelling_uuid(dwelling_uuid):
    result = CON.execute(
        "SELECT d.* FROM hubs h inner join devices d on h.uuid = d.hub_uuid WHERE h.dwelling_uuid = ?;",
        (dwelling_uuid,),
    ).fetchall()
    return result
