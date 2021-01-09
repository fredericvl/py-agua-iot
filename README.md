# py-agua-iot

py-agua-iot provides controlling heating devices connected via the IOT Agua platform of Micronova.

**Warning: this module is not tested with multiple devices, there is no guarantee that it will work with your heating device.**

## Example usage

```
from py_agua_iot import agua_iot

# https://evastampaggi.agua-iot.com = Agua IOT API URL for Eva Calor
# 635987 = customer code of Eva Calor
# 1c3be3cd-360c-4c9f-af15-1f79e9ccbc2a = random UUID (you can generate one here: https://www.uuidgenerator.net/version4)
connection = agua_iot("https://evastampaggi.agua-iot.com", "635987", "john.smith@gmail.com", "mysecretpassword", "1c3be3cd-360c-4c9f-af15-1f79e9ccbc2a")

# Print the current air temperature for each device
for device in connection.devices:
  print(device.name + ": " + str(device.air_temperature))
```

## Other examples

### Home Assistant

See [examples/home-assistant/README.md](examples/home-assistant/README.md)