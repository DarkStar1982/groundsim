# Groundsim API reference
## Satellite List
**URL:** {GROUND_SIM_HOST}/list

**Request type:** HTTP GET

**Response Type:** JSON<br/>
```
{
  "status": "ok",
  "satelites": [
    {"sat_name": "USA224", "norad_id": 37348}
  ]
}
```
## Initialization
**URL:** {GROUND_SIM_HOST}/mse_init/?norad_id=37348&date=2019,02,04,14,45,45

**Request type:** HTTP GET

**Parameters:**
* norad_id - satellite id in the database
* date - mission start date

**Response Type:** JSON<br/>

**Response Data**: Initial mission simulation state

## Simulation Control
**URL:** {GROUND_SIM_HOST}/mse_step/?steps=1

**Request type:** HTTP POST<br/>

**Request data:** Mission simulation state at step X

**Parameters:**
* steps - number of seconds to step forward

**Response Type:** JSON <br/>

**Response Data**: Mission simulation state at step X+ steps
