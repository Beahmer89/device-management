from device_management import device, fake_api

DWELLING_STATUSES = ["Occupied", "Vacant"]


def install_hub(hub_uuid=None, dwelling_uuid=None):
    if dwelling_uuid is None:
        dwelling_uuid = fake_api.create_dwelling()
    else:
        dwelling = fake_api.get_dwelling_by_uuid(dwelling_uuid=dwelling_uuid)
        if not dwelling:
            return "", "Dwelling Not Found"
        dwelling_uuid = dwelling[0]

    if not hub_uuid:
        hub_uuid = fake_api.create_hub()
    else:
        hub = fake_api.get_hub_by_uuid(hub_uuid=hub_uuid)
        if not hub:
            return "", "Hub Not Found"

        existing_hub_uuid = hub[3]
        if existing_hub_uuid:
            return "", "Hub Already Installed"
        hub_uuid = hub[0]

    request_json = {"dwelling_uuid": dwelling_uuid}

    hub_uuid = fake_api.update_hub_with_dwelling_uuid(
        hub_uuid=hub_uuid, request_data=request_json
    )
    return str(hub_uuid[0]), None


def list_dwellings(limit=10, offset=0):
    devices = fake_api.get_all_dwellings(limit, offset)
    return devices, None


def resident_moved_out(dwelling_uuid):
    # get dwellings devices
    devices = fake_api.get_devices_by_dwelling_uuid(
        dwelling_uuid=dwelling_uuid
    )
    request_json = {"status": "Vacant"}
    fake_api.update_dwelling_status_by_uuid(dwelling_uuid, request_json)

    # set devices to initial_value
    for dwelling_device in devices:
        device_uuid = dwelling_device[0]
        device_type = dwelling_device[1]
        device_type_info = device.DEVICE_TYPES[device_type]
        initial_state = device_type_info["initial_state"]

        device.update_state(device_uuid=device_uuid, state=initial_state)

    return True, None


def resident_moved_in(dwelling_uuid, create_hub=False):
    devices = fake_api.get_devices_by_dwelling_uuid(
        dwelling_uuid=dwelling_uuid
    )
    request_json = {"status": "Occupied"}
    fake_api.update_dwelling_status_by_uuid(dwelling_uuid, request_json)

    if not devices and create_hub:
        hub_uuid, error = install_hub(dwelling_uuid=dwelling_uuid)

    # could add logic to pair devices

    return True, None
