import uuid

from device_management import device, hub, dwelling


def test_install_hub(db_connection):
    hub_uuid, error = dwelling.install_hub()

    installed_hub = db_connection.execute(
        "SELECT * FROM hubs WHERE uuid = ?", (hub_uuid,)
    ).fetchone()

    assert installed_hub[1] is not None


def test_install_hub_already_installed(db_connection):
    hub_uuid, error = dwelling.install_hub()
    hub_uuid, error = dwelling.install_hub(hub_uuid=hub_uuid)

    assert hub_uuid == ""
    assert error == "Hub Already Installed"


def test_install_hub_unknown_hub_uuid(db_connection):
    hub_uuid = str(uuid.uuid4())
    hub_uuid, error = dwelling.install_hub(hub_uuid=hub_uuid)

    assert hub_uuid == ""
    assert error == "Hub Not Found"


def test_install_hub_unknown_hub_uuid(db_connection):
    dwelling_uuid = str(uuid.uuid4())
    hub_uuid, error = dwelling.install_hub(dwelling_uuid=dwelling_uuid)

    assert hub_uuid == ""
    assert error == "Dwelling Not Found"


def test_list_dwellings(db_connection):
    hub_uuid, error = dwelling.install_hub()
    hub_uuid, error = dwelling.install_hub()

    dwellings = dwelling.list_dwellings(limit=2)

    assert len(dwellings) == 2


def test_resident_moved_out_successfully(db_connection, create_dwelling):
    dwelling_uuid = create_dwelling
    hub_uuid, error = dwelling.install_hub(dwelling_uuid=dwelling_uuid)
    device_type = "switch"
    device_type1 = "lock"
    switch_device_uuid, error = device.create_device(device_type=device_type)
    lock_device_uuid, error = device.create_device(device_type=device_type1)

    _, error = hub.pair_device(device_uuid=switch_device_uuid, hub_uuid=hub_uuid)
    assert error is None
    _, error = hub.pair_device(device_uuid=lock_device_uuid, hub_uuid=hub_uuid)
    devices_for_hub = db_connection.execute(
        "SELECT * FROM devices WHERE hub_uuid = ?", (hub_uuid,)
    ).fetchall()
    assert len(devices_for_hub) == 2

    assert error is None
    device.update_state(device_uuid=switch_device_uuid, state="on")
    device.update_state(device_uuid=lock_device_uuid, state="open")

    lock_device_before = db_connection.execute(
        "SELECT * FROM devices WHERE uuid = ?", (lock_device_uuid,)
    ).fetchone()

    switch_device_before = db_connection.execute(
        "SELECT * FROM devices WHERE uuid = ?", (switch_device_uuid,)
    ).fetchone()

    dwelling.resident_moved_out(dwelling_uuid=dwelling_uuid)

    lock_device_after = db_connection.execute(
        "SELECT * FROM devices WHERE uuid = ?", (lock_device_uuid,)
    ).fetchone()
    switch_device_after = db_connection.execute(
        "SELECT * FROM devices WHERE uuid = ?", (switch_device_uuid,)
    ).fetchone()

    assert lock_device_before[2] != lock_device_after[2]
    assert lock_device_before[2] != lock_device_after[2]


def test_resident_moved_out_no_hub(db_connection, create_dwelling):
    dwelling_uuid = create_dwelling

    dwelling.resident_moved_out(dwelling_uuid=dwelling_uuid)


def test_resident_moved_out_no_devices(db_connection, create_dwelling):
    dwelling_uuid = create_dwelling
    hub_uuid, error = dwelling.install_hub(dwelling_uuid=dwelling_uuid)
    dwelling.resident_moved_out(dwelling_uuid=dwelling_uuid)
