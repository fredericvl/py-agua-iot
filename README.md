# py-agua-iot

py-agua-iot provides controlling heating devices connected via the IOT Agua platform of Micronova.

**Warning: this module is not tested with multiple devices, there is no guarantee that it will work with your heating device.**

## Example usage

```
from py_agua_iot import agua_iot

# https://evastampaggi.agua-iot.com => Agua IOT API URL for Eva Calor
# 635987 => customer code of Eva Calor
# 1c3be3cd-360c-4c9f-af15-1f79e9ccbc2a => random UUID (you can generate one here: https://www.uuidgenerator.net/version4)
# brand_id="1" => optional brand id (should always be "1" but can be overridden just in case)
# login_api_url="" => optional separate login URL (used for Piazzetta for example)
connection = agua_iot("https://evastampaggi.agua-iot.com", "635987", "john.smith@gmail.com", "mysecretpassword", "1c3be3cd-360c-4c9f-af15-1f79e9ccbc2a", brand_id="1")

# Print the current air temperature for each device
for device in connection.devices:
  print(device.name + ": " + str(device.air_temperature))
```

## API URL's / Customer codes

Below you can find a table with the app names of the different stove brands and their corresponding customer code and API URL.

| App name or Brand             | Customer Code | API URL                                | Separate login URL (only needed if specified)         |
| ----------------------------- | ------------- | -------------------------------------- | ----------------------------------------------------- |
| EvaCalòr - PuntoFuoco         | 635987        | https://evastampaggi.agua-iot.com      |                                                       |
| Elfire Wifi                   | 402762        | https://elfire.agua-iot.com            |                                                       |
| Karmek Wifi                   | 403873        | https://karmekone.agua-iot.com         |                                                       |
| Easy Connect                  | 354924        | https://remote.mcz.it                  |                                                       |
| Easy Connect Plus             | 746318        | https://remote.mcz.it                  |                                                       |
| Easy Connect Poêle            | 354925        | https://remote.mcz.it                  |                                                       |
| Lorflam Home                  | 121567        | https://lorflam.agua-iot.com           |                                                       |
| LMX Remote Control            | 352678        | https://laminox.agua-iot.com           |                                                       |
| Boreal Home                   | 173118        | https://boreal.agua-iot.com            |                                                       |
| Bronpi Home                   | 164873        | https://bronpi.agua-iot.com            |                                                       |
| EOSS WIFI                     | 326495        | https://solartecnik.agua-iot.com       |                                                       |
| LAMINOXREM REMOTE CONTROL 2.0 | 352678        | https://laminox.agua-iot.com           |                                                       |
| Jolly Mec Wi Fi               | 732584        | https://jollymec.agua-iot.com          |                                                       |
| Globe-fire                    | 634876        | https://globefire.agua-iot.com         |                                                       |
| TS Smart                      | 046629        | https://timsistem.agua-iot.com         |                                                       |
| Stufe a pellet Italia         | 015142        | https://stufepelletitalia.agua-iot.com |                                                       |
| My Corisit                    | 101427        | https://mycorisit.agua-iot.com         |                                                       |
| Fonte Flamme contrôle 1       | 848324        | https://fonteflame.agua-iot.com        |                                                       |
| Klover Home                   | 143789        | https://klover.agua-iot.com            |                                                       |
| Nordic Fire 2.0               | 132678        | https://nordicfire.agua-iot.com        |                                                       |
| GO HEAT                       | 859435        | https://amg.agua-iot.com               |                                                       |
| Wi-Phire                      | 521228        | https://lineavz.agua-iot.com           |                                                       |
| Thermoflux                    | 391278        | https://thermoflux.agua-iot.com        |                                                       |
| Darwin Evolution              | 475219        | https://cola.agua-iot.com              |                                                       |
| Moretti design                | 624813        | https://moretti.agua-iot.com           |                                                       |
| Fontana Forni                 | 505912        | https://fontanaforni.agua-iot.com      |                                                       |
| MyPiazzetta (MySuperior?)     | 458632        | https://piazzetta.agua-iot.com         | https://piazzetta.iot.web2app.it/api/bridge/endpoint/ |
| Alfaplam                      | 862148        | https://alfaplam.agua-iot.com          |                                                       |
| Nina                          | 999999        | https://micronova.agua-iot.com         |                                                       |
| Galletti                      | ?             | ?                                      |                                                       |

If you happen to know any extra or missing customer codes and API URL's, please feel free to open a pull request and add them to the table above.

## Other examples

### Home Assistant

See [examples/home-assistant/README.md](examples/home-assistant/README.md)
