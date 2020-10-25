
# MISSION SIMULATION ENVIRONMENT DESCRIPTION

## Environment Simulation Parameters
| Environment Inputs | Environment Outputs | 
| :------------- | :----------: |
| Orbital vector	 |	Ground track lat/lon   | 
| Sun vector | Day/night phase |
| Magnetic field vector | 	Ground station visibility |
| Ground stations list |Thermal power input |
| **Constants** | Visible light input |
| Visible light irradiation scalar | 	Ground station visibility |
| Magnetic field vector | |
| Thermal irradiation scalar | |
  
## Satellite Simulation Parameters

| **Internal Inputs** | **Outputs** | 
| :------------- | :----------: |
| Solar Panel Power Out	 | Solar Panel Power Out | 
| Attitude vector | Attitude vector |
| Battery Power In | Battery Power In |
| Battery Power Out | Battery Power Out |
| Battery Capacity Left | Battery Capacity Left | 
| Camera Power Draw |Camera Power Draw | 
| SDR Power Draw | SDR Power Draw | 
| ADCS Power Draw | ADCS Power Draw | 	
| ADCS Power Draw | ADCS Power Draw | 
| Thermal sensors data | Thermal sensors data | 
| Instrument states | Instrument states | 
| Storage queues | Storage queues | 
| **External inputs** | | 
| Camera buffer | | 	
| SDR input buffer | |		
| Uplink command buffer | |
| **Constants** | |
| Satellite geometry | |	
| Satellite TLE | |	
| Satellite configuration | |	
	

## Architecture
* Backend: API HTTP server + satellite simulator as standalone module
   * DB schema: work in-progress
   * Frontend: Vue.js + jQuery
* Workflow
* Frontend:
    * calls “initialize” API and then calls “step forward” API repeatedly
    * Simulation instance data is stored on the frontend (client-side)
    * On each “step” call simulation instance is sent towards the server
* Server:
    * Creates initial simulation instance after “initialize” called.
    * Steps simulation instance forward in time after “step forward” call.
    * Receives data from front-end, steps in forward in time and returns back to front-end

## Satellite simulation - features/subsystems notes
* Payload APIs
    * Camera
        * Get image frame
        * Make a shot 
    * SDR
        * Set receiver parameters
        * Start recording
        * Stop recording
    * ADCS
        * Change attitude mode
        * Desaturate RCS
    * COMM
        * Get telemetry
        * Upload mission script
        * Download science data
* Subsystem behavior
    * Geometry & mass
        * Important for ADCS
        * All subsystems are modelled as blocks
    * Power subsystem
        * Current/voltage/power draw simulation
        * Thermal dissipation
    * Thermal subsystem
        * Use nodal model
    * OBDH (take runtime from OPS_SAT)
    * COMM (include ground station visibility)

## Environment & satellite simulation - TODO
* Add night-day functionality.
* Add irradiation conditions (beta angle, thermals, etc)
* Add proper orbit simulation?
* Add ADCS functionality (how to use quaternions??)
* Share mission functionality (add screen to enter email to get mission url with hash) 

## Mission Scenarios - TODO
* Save/Resume logic
    * First save is a "save as..."
    	* Create unique mission hash/create database object
        * Prompts a modal with name/email to register, saves into the database
	* Then send an email to the user with an url to load saved mission
    * Second and subsequent saves just update the saved mission 
* On each step, update mission simulation object
* Take examples from VEGA MiniSim for scenarios

## Example mission scenarios - TODO
* Imager missions
    * take photo on the ground
    * take photo of celestial object
    * take photo of another satellite
* SDR missions
    * AIS intercept
    * ADS-B intercept
    * “Other satellite” transmission intercept


