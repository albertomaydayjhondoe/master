def test_device_manager_import():
    from device_farm.controllers.device_manager import DeviceManager

    dm = DeviceManager()
    devices = dm.list()
    assert isinstance(devices, list)
    # perform a dummy action on the first device
    first = devices[0]["id"]
    res = dm.perform_action(first, "tap", {"x": 100, "y": 200})
    assert res.get("success") is True
