import uuid
import os

import duckdb
from device_management import device

if os.path.exists("test_db.duckdb"):
    os.remove("test_db.duckdb")
con = duckdb.connect(database="test_db.duckdb")
con.sql("CREATE TABLE dwelling (uuid UUID, name string)")
con.sql("""
        CREATE TABLE hubs (uuid UUID PRIMARY KEY DEFAULT UUID(), name string)
        """)
con.sql(
    """
        CREATE TABLE devices (
        uuid UUID PRIMARY KEY DEFAULT UUID(),
        type TEXT NOT NULL,
        state TEXT NOT NULL,
        hub_uuid UUID REFERENCES hubs(uuid)
       )"""
)


def test_create_device_known_type():
    device_type = "switch"
    device_uuid = device.create_device(device_type=device_type)
    device_created = con.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()

    assert device_uuid == str(device_created[0])
    assert device_created[1] == device_type


def test_create_device_type_numeral_state():
    device_type = "dimmer"
    device_uuid = device.create_device(device_type=device_type)
    device_created = con.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()

    assert device_uuid == str(device_created[0])
    assert device_created[1] == device_type


def test_create_device_unknown_type():
    device_type = "alexa"
    device_uuid = device.create_device(device_type=device_type)
    device_created = con.execute(
        "SELECT * FROM devices WHERE type = ?", (device_uuid,)
    ).fetchone()

    assert device_created is None
    assert device_uuid == f"Cannot Create Device of Type: {device_type}"


def test_delete_device():
    device_type = "thermostat"
    device_uuid = device.create_device(device_type=device_type)

    device.delete_device(device_uuid=device_uuid)
    device_created = con.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()
    assert device_created is None


def test_get_device_state():
    device_type = "switch"
    device_uuid = device.create_device(device_type=device_type)

    device_state = device.get_state(device_uuid=device_uuid)
    device_created = con.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()

    assert device_state == device_created[2]


def test_get_device_state_unknown_uuid():
    unknown_uuid = str(uuid.uuid4())
    device_state = device.get_state(device_uuid=unknown_uuid)

    assert device_state == ""


def test_patch_device_state():
    device_type = "lock"
    new_state = "open"
    device_uuid = device.create_device(device_type=device_type)

    device.update_state(device_uuid=device_uuid, state=new_state)
    device_created = con.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()
    assert device_created[2] == new_state


def test_patch_thermostate_device_state():
    device_type = "thermostat"
    new_state = "71"
    device_uuid = device.create_device(device_type=device_type)

    device.update_state(device_uuid=device_uuid, state=new_state)
    device_created = con.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()
    assert device_created[2] == new_state


def test_patch_device_bad_state():
    device_type = "switch"
    new_state = "middle"
    device_uuid = device.create_device(device_type=device_type)

    device.update_state(device_uuid=device_uuid, state=new_state)
    device_created = con.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()
    assert device_created[2] != new_state


def test_get_devices():
    device_type = "switch"
    device.create_device(device_type=device_type)
    device.create_device(device_type=device_type)
    device.create_device(device_type=device_type)

    devices = device.get_devices(limit=2)

    assert len(devices) == 2
