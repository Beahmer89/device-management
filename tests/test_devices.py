import uuid

from device_management import device


def test_create_device_known_type(db_connection):
    device_type = "switch"
    device_uuid, error = device.create_device(device_type=device_type)
    device_created = db_connection.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()

    assert error is None
    assert device_uuid, error == str(device_created[0])
    assert device_created[1] == device_type


def test_create_device_type_numeral_state(db_connection):
    device_type = "dimmer"
    device_uuid, error = device.create_device(device_type=device_type)
    device_created = db_connection.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()

    assert error is None
    assert device_uuid == str(device_created[0])
    assert device_created[1] == device_type


def test_create_device_unknown_type(db_connection):
    device_type = "alexa"
    device_uuid, error = device.create_device(device_type=device_type)
    device_created = db_connection.execute(
        "SELECT * FROM devices WHERE type = ?", (device_uuid,)
    ).fetchone()

    assert device_created is None
    assert error == f"Cannot Create Device of Type: {device_type}"


def test_delete_device(db_connection):
    device_type = "thermostat"
    device_uuid, error = device.create_device(device_type=device_type)

    device.delete_device(device_uuid=device_uuid)
    device_created = db_connection.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()
    assert device_created is None


def test_get_device_state(db_connection):
    device_type = "switch"
    device_uuid, error = device.create_device(device_type=device_type)

    device_state, error = device.get_state(device_uuid=device_uuid)
    device_created = db_connection.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()

    assert error is None
    assert device_state == device_created[2]


def test_get_device_state_unknown_uuid(db_connection):
    unknown_uuid = str(uuid.uuid4())
    device_state, error = device.get_state(device_uuid=unknown_uuid)

    assert error == "Device Not Found"
    assert device_state == ""


def test_patch_device_state(db_connection):
    device_type = "lock"
    new_state = "open"
    device_uuid, error = device.create_device(device_type=device_type)

    device.update_state(device_uuid=device_uuid, state=new_state)
    device_created = db_connection.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()
    assert device_created[2] == new_state


def test_patch_thermostate_device_state(db_connection):
    device_type = "thermostat"
    new_state = "71"
    device_uuid, error = device.create_device(device_type=device_type)

    device.update_state(device_uuid=device_uuid, state=new_state)
    device_created = db_connection.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()
    assert device_created[2] == new_state


def test_patch_device_bad_state(db_connection):
    device_type = "switch"
    new_state = "middle"
    device_uuid, error = device.create_device(device_type=device_type)

    device.update_state(device_uuid=device_uuid, state=new_state)
    device_created = db_connection.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()
    assert device_created[2] != new_state


def test_get_devices(db_connection):
    device_type = "switch"
    device.create_device(device_type=device_type)
    device.create_device(device_type=device_type)
    device.create_device(device_type=device_type)

    devices, error = device.get_devices(limit=2)

    assert error is None
    assert len(devices) == 2
