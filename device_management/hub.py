from device_management import fake_api


def pair_device(device_uuid, hub_uuid):
    hub_uuid = fake_api.get_hub_by_uuid(hub_uuid=hub_uuid)

    if not hub_uuid:
        return False, "Could not find/create hub"

    device = fake_api.get_device_by_uuid(device_uuid)
    if not device:
        return False, "Device Not Found"

    existing_hub_uuid = device[3]
    if existing_hub_uuid:
        return False, "Device is already paired"

    request_json = {"hub_uuid": hub_uuid}

    fake_api.update_device_pairing_by_uuid(
        device_uuid=device_uuid, request_data=request_json
    )
    return True, None


def get_device_state(device_uuid, hub_uuid):
    result = fake_api.get_device_by_hub_and_device_uuid(
        device_uuid=device_uuid, hub_uuid=hub_uuid
    )
    if not result:
        return "", "Could not find device state"

    device_state = result[2]
    return device_state, None


def list_hub_devices(hub_uuid):
    hub_devices = fake_api.get_devices_by_hub(hub_uuid=hub_uuid)

    if not hub_devices:
        return [], None

    return hub_devices, None


def unpair_device(device_uuid):
    device = fake_api.get_device_by_uuid(device_uuid)
    if not device:
        return None, "Device not found"

    fake_api.unpair_device_by_uuid(
        device_uuid=device_uuid,
    )
    return None, None
