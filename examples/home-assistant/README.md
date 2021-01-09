# Custom component integration in Home Assistant

**Warning: this integration is not tested with multiple devices, there is no guarantee that it will work with your Agua IOT heating device.\
It's also not guaranteed that this custom component will keep on working in future Home Assistant releases due to architectural changes for example.**

This custom component has been tested with Home Assistant 2020.12.1 and one Agua IOT heating device (Eva Calor stove).

## Installation

1. If it does not already exist, create a `custom_components` directory in your Home Assistant config directory
1. Copy the [aguaiot](custom_components/aguaiot) folder and its contents into the `custom_components` directory within your Home Assistant config directory.
1. Restart Home Assistant to load the custom component.
2. Open the Home Assistant web interface and go to `Integrations` and add the `Micronova Agua IOT` integration using the Agua IOT API url and customer code of the brand of your heating device, and the email address and password that you use to login and manage your Agua IOT heating device.

After following the steps above you should now be able to see your heating device as a device in Home Assistant.