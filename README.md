# Groundsim API reference
## Initialization
URL: {GROUND_SIM_HOST}/mse_init/?norad_id=37348&date=2019,02,04,14,45,45
Request type: HTTP GET
Parameters:
* norad_id - satellite id in the database
* date - mission start date
Response: JSON
"OK"/Error

## Simulation Control
URL: {GROUND_SIM_HOST}/mse_step/?steps=1
Request type: HTTP GET
Parameters:
* steps - number of seconds to step forward
Response: JSON
"OK"/Error

## Location
URL: {GROUND_SIM_HOST}/location
Request type: HTTP GET
Response: JSON
{
    "status":"ok/error",
    "error":"{error message}",
    "lat":47.9898098,
    "lng":-79.56565665,
    "alt":455.2,
    "a":6826.2,
    "e":0.0026,
    "i":55.76,
    "ra":116.44,
    "w":74.91,
    "tp":3141,
    "time":"23:35:21GMT 11 June 2019"
}

## Telemetry
URL: {GROUND_SIM_HOST}/telemetry
Request type: HTTP GET
Response: JSON
{
    "status": "ok/error",
    "error": "{error message}",
    "power": [
        {
            "param": "Parameter label/name",
            "value": "parameter value"
        },
        {
            "param": "Parameter label/name",
            "value": "parameter value"
        },
        {
            "param": "Parameter label/name",
            "value": "parameter value"
        },
        {
            "param": "Parameter label/name",
            "value": "parameter value"
        }
    ],
    "thermal": [
        {
            "param": "Parameter label/name",
            "value": "parameter value"
        },
        {
            "param": "Parameter label/name",
            "value": "parameter value"
        },
        {
            "param": "Parameter label/name",
            "value": "parameter value"
        },
        {
            "param": "Parameter label/name",
            "value": "parameter value"
        }
    ],
    "obdh": [
