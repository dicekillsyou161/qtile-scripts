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
        if temp_value <	30.00:
        	self.layout.colour = "#21e7e0"
        elif temp_value <=	33.25:
        	self.layout.colour = "#1fe8c3"
        elif temp_value <=	36.50:
        	self.layout.colour = "#1ee9a6"
        elif temp_value <=	39.75:
        	self.layout.colour = "#1cea87"
        elif temp_value <=	43.00:
        	self.layout.colour = "#1bec68"
        elif temp_value <=	46.25:
        	self.layout.colour = "#19ed48"
        elif temp_value <=	49.50:
        	self.layout.colour = "#17ee27"
        elif temp_value <=	52.75:
        	self.layout.colour = "#26ef16"
        elif temp_value <=	56.00:
        	self.layout.colour = "#45f014"
        elif temp_value <=	59.25:
        	self.layout.colour = "#65f212"
        elif temp_value <=	62.50:
        	self.layout.colour = "#86f311"
        elif temp_value <=	65.75:
        	self.layout.colour = "#a8f40f"
        elif temp_value <=	69.00:
        	self.layout.colour = "#caf50d"
        elif temp_value <=	72.25:
        	self.layout.colour = "#eef60c"
        elif temp_value <=	75.50:
        	self.layout.colour = "#f8dd0a"
        elif temp_value <=	78.75:
        	self.layout.colour = "#f9bb08"
        elif temp_value <=	82.00:
        	self.layout.colour = "#fa9707"
        elif temp_value <=	85.25:
        	self.layout.colour = "#fb7305"
        elif temp_value <=	88.50:
        	self.layout.colour = "#fd4d03"
        elif temp_value <=	91.75:
        	self.layout.colour = "#fe2702"
        else:
        	self.layout.colour = "#ff0000"
        return text
