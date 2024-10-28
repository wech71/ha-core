"""Factory and mocking instance of Editmax SmartPlug for testing purposes."""

from pyedimax.smartplug import SmartPlug


class HardwareApiFactory:
    """Class Factory for SmartPlug."""

    @staticmethod
    def create_smart_plug(host, auth=("admin", "1234")) -> SmartPlug:
        """Create SmartPlug or MockedSmartPlug instance for easier debugging."""

        # return SmartPlug(host, auth)
        return MockedSmartPlug(host, auth)


class MockedSmartPlug(SmartPlug):
    """Representation an mocking of an edimax SmartPlug api."""

    # pylint: disable=super-init-not-called
    def __init__(self, host: str, auth) -> None:
        """Create a new SmartPlug instance identified by the given URL.

        :rtype : object
        :param host: The IP/hostname of the SmartPlug. E.g. '172.16.100.75'
        :param auth: User and password to authenticate with the plug. E.g. ('admin', '1234')
        """

        # we must not call base class as it would make a tcp connection
        # super().__init__(host, auth)
        self.auth = auth

    _state = "OFF"

    @property
    def state(self):
        """Get the current state of the SmartPlug.

        :type self: object
        :rtype: str
        :return: 'ON' or 'OFF'
        """

        return self._state

    @state.setter
    def state(self, value):
        """Set the state of the SmartPlug.

        :type self: object
        :type value: str
        :param value: 'ON', 'on', 'OFF' or 'off'
        """

        if value not in ("ON", "on", "OFF", "off"):
            raise MockedSmartPlugException(
                "Failed to communicate with SmartPlug: Invalid Value"
            )
        self._state = value

    @property
    def now_power(self):
        """Get the current power in watts of the SmartPlug. Only works on SP-2101W.

        :type self: object
        :rtype: float
        :return: Current power usage in watts
        """
        return 10

    @property
    def now_energy_day(self):
        """Get the power for the day in kwh for the SmartPlug. Only works on SP-2101W.

        :type self: object
        :rtype: float
        :return: Current power usage for the day in kwh
        """

        return 1000

    @property
    def info(self):
        """Get device info (vendor, model, version, mac and system name (if available)).

        :type self:     object
        :rtype:         dictionary
        :return:        dictionary with the following keys: vendor, model, version, mac, name
        """

        return {
            "mac": "00:00:00:01",
            "vendor": "edimax",
            "model": "mocked",
            "version": 1.0,
            "name": "SmartPlug",
        }


class MockedSmartPlugException(Exception):
    """Custom Exception for MockedSmartPlug."""
