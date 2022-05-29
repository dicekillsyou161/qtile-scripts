import psutil

from libqtile.widget import base


#[docs]
class ThermalSensorCC(base.InLoopPollText):
    """Widget to display temperature sensor information

    For using the thermal sensor widget you need to have lm-sensors installed.
    You can get a list of the tag_sensors executing "sensors" in your terminal.
    Then you can choose which you want, otherwise it will display the first
    available.

    Widget requirements: psutil_.

    .. _psutil: https://pypi.org/project/psutil/
    """

    defaults = [
        ("metric", True, "True to use metric/C, False to use imperial/F"),
        ("show_tag", False, "Show tag sensor"),
        ("update_interval", 2, "Update interval in seconds"),
        ("tag_sensor", None, 'Tag of the temperature sensor. For example: "temp1" or "Core 0"'),
        (
            "threshold",
            70,
            "If the current temperature value is above, "
            "then change to foreground_alert colour",
        ),
        ("foreground_alert", "ff0000", "Foreground colour alert"),
    ]

    def __init__(self, **config):
        base.InLoopPollText.__init__(self, **config)
        self.add_defaults(ThermalSensorCC.defaults)
        temp_values = self.get_temp_sensors()
        self.foreground_normal = self.foreground

        if temp_values is None:
            self.data = "sensors command not found"
        elif len(temp_values) == 0:
            self.data = "Temperature sensors not found"
        elif self.tag_sensor is None:
            for k in temp_values:
                self.tag_sensor = k
                break

    def get_temp_sensors(self):
        """
        Reads temperatures from sys-fs via psutil.
        Output will be read Fahrenheit if user has specified it to be.
        """

        temperature_list = {}
        temps = psutil.sensors_temperatures(fahrenheit=not self.metric)
        unit = "°C" if self.metric else "°F"
        empty_index = 0
        for kernel_module in temps:
            for sensor in temps[kernel_module]:
                label = sensor.label
                if not label:
                    label = "{}-{}".format(
                        kernel_module if kernel_module else "UNKNOWN", str(empty_index)
                    )
                    empty_index += 1
                temperature_list[label] = (str(round(sensor.current, 1)), unit)

        return temperature_list

    def poll(self):
        temp_values = self.get_temp_sensors()
        if temp_values is None:
            return False
        text = ""
        if self.show_tag and self.tag_sensor is not None:
            text = self.tag_sensor + ": "
        text += "".join(temp_values.get(self.tag_sensor, ["N/A"]))
        temp_value = float(temp_values.get(self.tag_sensor, [0])[0])        
        if temp_value < 30.0:
            self.layout.colour = "#2dc2b3"
        elif temp_value <= 40.0:
            self.layout.colour = "#2dc289"          
        elif temp_value <= 50.0:
            self.layout.colour = "#2dc261"
        elif temp_value < 55.0:
            self.layout.colour = "#2dc234"
        elif temp_value < 60:
            self.layout.colour = "#4fc22d"
        elif temp_value < 65:
            self.layout.colour = "#7ac22d"
        elif temp_value < 70:
            self.layout.colour = "#a1c22d"
        elif temp_value < 75:
            self.layout.colour = "#c2b82d"
        elif temp_value < 80:
            self.layout.colour = "#c2932d"
        elif temp_value < 85:
            self.layout.colour = "#c2722d"
        else: #temp_value >= 85:
            self.layout.colour = "#c2372d"
        return text
