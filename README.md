# Groundsim API reference
## Initialization
### URL: {GROUND_SIM_HOST}/mse_init/?norad_id=37348&date=2019,02,04,14,45,45
### Request type: HTTP GET
### Parameters:
* norad_id - satellite id in the database
* date - mission start date
### Response Type: JSON
"OK"/Error

## Simulation Control
**URL:** {GROUND_SIM_HOST}/mse_step/?steps=1
**Request type:** HTTP GET
**Parameters:**
* steps - number of seconds to step forward
**Response Type:** JSON
"OK"/Error

## Location
**URL:** {GROUND_SIM_HOST}/location
**Request type:** HTTP GET
**Response:** JSON
```
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
```

## Telemetry
**URL:** {GROUND_SIM_HOST}/telemetry
**Request type:** HTTP GET
**Response type:** JSON
```
{
    "status": "ok", 
    "power": {
        "battery_level": 100.0, 
        "battery_output": 0.0, 
        "battery_input": 0.0, 
        "solar_panel_output": 0.0
    }, 
    "thermal": {
        "chassis_temp": 0.0, 
        "solar_panel_temp": 0.0, 
        "obdh_board_temp": 0.0, 
        "battery_temp": 0.0
    }, 
    "obdh": {
        "obdh_status": "OK",
        "cpu_load": 0.0,
        "storage_capacity": 100.0, 
        "tasks_running": []
    }, 
    "adcs": {
        "gyro_rpm": 0, 
        "attitude_mode": 
        "SUN_POINTING", 
        "adcs_status": "OK", 
        "adcs_vectors": []
     }
   }
   ```
