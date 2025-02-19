from device_management import fake_api


DEVICE_TYPES = {
    "dimmer": {"state": ["number"], "initial_state": "0"},
    "switch": {"state": ["on", "off"], "initial_state": "off"},
    "lock": {"state": ["open", "shut"], "initial_state": "shut"},
    "thermostat": {"state": ["number"], "initial_state": "0"},
}


def create_device(device_type):
    try:
        device_state = DEVICE_TYPES[device_type]
        json_body = {
            "type": device_type,
            "state": device_state["initial_state"],
        }
        device_uuid = fake_api.create_device(json_body)
    except KeyError:
        return "", f"Cannot Create Device of Type: {device_type}"

    return device_uuid, None


def delete_device(device_uuid):
    device = fake_api.get_device_by_uuid(device_uuid)
    if not device:
        return None, "Device not found"

    device_hub = device[3]
    if device_hub:
        return None, "Device is paired"

    fake_api.delete_device_by_uuid(device_uuid)
    return None, None


def get_state(device_uuid):
    device = fake_api.get_device_by_uuid(device_uuid)
    if not device:
        return "", "Device Not Found"

    device_state = device[2]
    return device_state, None


def update_state(device_uuid, state):
    device = fake_api.get_device_by_uuid(device_uuid)
    device_type = device[1]

    device_state = DEVICE_TYPES[device_type]
    if state in device_state["state"] or state.isnumeric():
        json_body = {"state": state}
        fake_api.update_device_by_uuid(
            device_uuid=device_uuid, request_data=json_body
        )
        return True, None

    return False, None


def get_devices(limit=10, offset=0):
    devices = fake_api.get_all_devices(limit, offset)
    return devices, None
