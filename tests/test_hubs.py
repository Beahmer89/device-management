import uuid

from device_management import device, dwelling, hub


def test_pairing_device_without_hub(db_connection):
    hub_uuid, error = dwelling.install_hub()
    device_type = "switch"
    device_uuid, error = device.create_device(device_type=device_type)

    hub.pair_device(device_uuid=device_uuid, hub_uuid=hub_uuid)

    paired_device = db_connection.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()
    assert paired_device[3] is not None


def test_pairing_device_without_device(db_connection):
    hub_uuid, error = dwelling.install_hub()
    device_uuid = str(uuid.uuid4())

    paired, error = hub.pair_device(device_uuid=device_uuid, hub_uuid=hub_uuid)

    assert paired == False
    assert error == "Device Not Found"


def test_pairing_multiple_devices(db_connection):
    hub_uuid, error = dwelling.install_hub()
    device_type = "switch"
    device_type1 = "lock"
    switch_device_uuid, error = device.create_device(device_type=device_type)
    lock_device_uuid, error = device.create_device(device_type=device_type1)

    paired_hub_uuid, error = hub.pair_device(
        device_uuid=switch_device_uuid, hub_uuid=hub_uuid
    )
    assert error is None
    paired_hub_uuid, error = hub.pair_device(
        device_uuid=lock_device_uuid, hub_uuid=hub_uuid
    )
    assert error is None

    paired_device_count = db_connection.execute(
        "SELECT count(*) FROM devices WHERE hub_uuid = ?", (hub_uuid,)
    ).fetchone()
    assert paired_device_count[0] == 2


def test_pairing_device_already_paired(db_connection):
    hub_uuid, error = dwelling.install_hub()
    device_type = "switch"
    device_type1 = "lock"
    switch_device_uuid, error = device.create_device(device_type=device_type)
    lock_device_uuid, error = device.create_device(device_type=device_type1)

    _, error = hub.pair_device(device_uuid=switch_device_uuid, hub_uuid=hub_uuid)
    assert error is None
    _, error = hub.pair_device(device_uuid=lock_device_uuid, hub_uuid=hub_uuid)
    assert error is None

    # associate 1 device with another
    paired, error = hub.pair_device(device_uuid=lock_device_uuid, hub_uuid=hub_uuid)
    assert paired == False
    assert error == "Device is already paired"


def test_pairing_device_with_noexistent_hub(db_connection):
    device_uuid = str(uuid.uuid4())
    hub_uuid = str(uuid.uuid4())
    paired, error = hub.pair_device(hub_uuid=hub_uuid, device_uuid=device_uuid)

    assert paired == False
    assert error == "Could not find/create hub"


def test_get_device_state(db_connection):
    hub_uuid, error = dwelling.install_hub()
    device_type = "lock"
    device_uuid, error = device.create_device(device_type=device_type)
    _, error = hub.pair_device(device_uuid=device_uuid, hub_uuid=hub_uuid)

    state, error = hub.get_device_state(device_uuid=device_uuid, hub_uuid=hub_uuid)

    paired_device = db_connection.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()

    assert paired_device[2] == state


def test_get_device_state_unknown_uuid(db_connection):
    hub_uuid, error = dwelling.install_hub()
    device_type = "lock"
    device_uuid, error = device.create_device(device_type=device_type)
    _, error = hub.pair_device(device_uuid=device_uuid, hub_uuid=hub_uuid)
    unknown_uuid = str(uuid.uuid4())

    state, error = hub.get_device_state(device_uuid=unknown_uuid, hub_uuid=hub_uuid)

    assert state == ""
    assert error == "Could not find device state"


def test_list_devices(db_connection):
    hub_uuid, error = dwelling.install_hub()
    device_type = "switch"
    device_type1 = "lock"
    switch_device_uuid, error = device.create_device(device_type=device_type)
    lock_device_uuid, error = device.create_device(device_type=device_type1)

    _, error = hub.pair_device(device_uuid=switch_device_uuid, hub_uuid=hub_uuid)
    assert error is None
    _, error = hub.pair_device(device_uuid=lock_device_uuid, hub_uuid=hub_uuid)
    assert error is None

    hub_devices, error = hub.list_hub_devices(hub_uuid=hub_uuid)

    paired_device_count = db_connection.execute(
        "SELECT count(*) FROM devices WHERE hub_uuid = ?", (hub_uuid,)
    ).fetchone()
    assert paired_device_count[0] == len(hub_devices)


def test_unpairing_device(db_connection):
    hub_uuid, error = dwelling.install_hub()
    device_type = "lock"
    device_uuid, error = device.create_device(device_type=device_type)

    _, error = hub.pair_device(device_uuid=device_uuid, hub_uuid=hub_uuid)
    paired_device = db_connection.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchall()

    assert paired_device[0][3] is not None

    result, error = hub.unpair_device(device_uuid)

    paired_device = db_connection.execute(
        "SELECT * FROM devices WHERE uuid = ?", (device_uuid,)
    ).fetchone()
    assert paired_device[3] is None


def test_unpairing_unknown_device(db_connection):
    device_uuid = str(uuid.uuid4())

    result, error = hub.unpair_device(device_uuid=device_uuid)

    assert result is None
    assert error == "Device not found"
