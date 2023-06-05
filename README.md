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

| App name or Brand             | Customer Code | API URL                                | API Version | Separate login URL (only needed if specified)           |
| ----------------------------- | ------------- | -------------------------------------- | ----------- | ------------------------------------------------------- |
| Alfaplam                      | 862148        | https://alfaplam.agua-iot.com          | 1.4.4.0     |                                                         |
| Boreal Home                   | 173118        | https://boreal.agua-iot.com            | 1.4.1       |                                                         |
| Bronpi Home                   | 164873        | https://bronpi.agua-iot.com            | 1.4.1       |                                                         |
| Darwin Evolution              | 475219        | https://cola.agua-iot.com              | 2.1.0.0     |                                                         |
| Easy Connect                  | 354924        | https://remote.mcz.it                  | 1.5.0.0     |                                                         |
| Easy Connect Plus             | 746318        | https://remote.mcz.it                  | 1.5.0.0     |                                                         |
| Easy Connect Poêle            | 354925        | https://remote.mcz.it                  | 1.5.0.0     |                                                         |
| Elfire Wifi                   | 402762        | https://elfire.agua-iot.com            | 1.4.4.0     |                                                         |
| EOSS WIFI                     | 326495        | https://solartecnik.agua-iot.com       | 1.4.4.0     |                                                         |
| EvaCalòr - PuntoFuoco         | 635987        | https://evastampaggi.agua-iot.com      | 1.4.4.0     |                                                         |
| Fontana Forni                 | 505912        | https://fontanaforni.agua-iot.com      | 1.4.4.0     |                                                         |
| Fonte Flamme contrôle 1       | 848324        | https://fonteflame.agua-iot.com        | 1.4.4.0     |                                                         |
| Galletti                      | ?             | ?                                      | ?           |                                                         |
| Globe-fire                    | 634876        | https://globefire.agua-iot.com         | 1.4.4.0     |                                                         |
| GO HEAT                       | 859435        | https://amg.agua-iot.com               | 1.4.4.0     |                                                         |
| Jolly Mec Wi Fi               | 732584        | https://jollymec.agua-iot.com          | 2.1.0.0     |                                                         |
| Karmek Wifi                   | 403873        | https://karmekone.agua-iot.com         | 1.4.4.0     |                                                         |
| Klover Home                   | 143789        | https://klover.agua-iot.com            | 2.1.0.0     |                                                         |
| LAMINOXREM REMOTE CONTROL 2.0 | 352678        | https://laminox.agua-iot.com           | 1.4.4.0     |                                                         |
| LMX Remote Control            | 352678        | https://laminox.agua-iot.com           | 1.4.4.0     |                                                         |
| Lorflam Home                  | 121567        | https://lorflam.agua-iot.com           | 2.1.0.0     |                                                         |
| MCZ                           | ??????        | https://remote.mcz.it                  | 1.5.0.0     |                                                         |
| Moretti design                | 624813        | https://moretti.agua-iot.com           | 1.4.4.0     |                                                         |
| My Corisit                    | 101427        | https://mycorisit.agua-iot.com         | 1.4.4.0     |                                                         |
| MyPiazzetta (MySuperior?)     | 458632        | https://piazzetta.agua-iot.com         | 1.5.0.0     | https://piazzetta-iot.app2cloud.it/api/bridge/endpoint/ |
| Nina                          | 999999        | https://micronova.agua-iot.com         | 1.4.4.0     |                                                         |
| Nobis-Fi                      | 700700        | https://nobis.agua-iot.com             | 2.1.0.0     |                                                         |
| Nordic Fire 2.0               | 132678        | https://nordicfire.agua-iot.com        | 2.1.0.0     |                                                         |
| Ravelli Wi-Fi                 | 953712        | https://aico.agua-iot.com              | 1.4.1       |                                                         |
| Stufe a pellet Italia         | 015142        | https://stufepelletitalia.agua-iot.com | 1.4.4.0     |                                                         |
| Thermoflux                    | 391278        | https://thermoflux.agua-iot.com        | 1.4.4.0     |                                                         |
| TS Smart                      | 046629        | https://timsistem.agua-iot.com         | 1.4.4.0     |                                                         |
| Wi-Phire                      | 521228        | https://lineavz.agua-iot.com           | 1.4.4.0     |                                                         |

Version info and API documentation could be found at API swagger URL for each brand. Swager is accessible at /api-docs (example: https://nobis.agua-iot.com/api-docs).
If you happen to know any extra or missing customer codes and API URL's, please feel free to open a pull request and add them to the table above.

## Other examples

### Home Assistant

Home Assistant plugin using this library: [home_assistant_micronova_agua_iot](https://github.com/vincentwolsink/home_assistant_micronova_agua_iot)
