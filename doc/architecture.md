
MISSION SIMULATION ENVIRONMENT DESCRIPTION

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
  
Satellite Simulation

| **Internal Inputs** | **Outputs** | 
| :------------- | :----------: |
| Solar Panel Power Out	 | Solar Panel Power Out | 
| Attitude vectors | 	Attitude vector |
| Battery Power In | Battery Power In |
| Ground stations list |Thermal power input |
| **Constants** | Visible light input |
| Visible light irradiation scalar | 	Ground station visibility |
| Magnetic field vector | |
| Thermal irradiation scalar | |

		
	


Battery Power Out	Battery Power Out
Battery Capacity Left	Battery Capacity Left
Camera Power Draw	Camera Power Draw
SDR Power Draw	SDR Power Draw
ADCS Power Draw	ADCS Power Draw
Thermal sensors	Temperature sensors
Instrument states	Instrument states
Storage queues	Storage queues
External inputs	
Camera buffer	
SDR input buffer	
Uplink command buffer	
Constants	
Satellite geometry	
Satellite TLE	
Satellite configuration	

Architecture
•	Backend: API HTTP server + satellite simulator as standalone module
o	DB schema: work in-progress
•	Frontend: Vue.js + jQuery
•	Workflow
o	Frontend:
	calls “initialize” API and then calls “step forward” API repeatedly
	Simulation instance data is stored on the frontend (client-side)
	On each “step” call simulation instance is sent towards the server
o	Server:
	Creates initial simulation instance after “initialize” called.
	Steps simulation instance forward in time after “step forward” call.
	Receives data from front-end, steps in forward in time and returns back to front-end

Satellite simulation features/subsystems features simulated
•	Payload APIs
o	Camera
	Get image frame
	Make a shot 
o	SDR
	Set receiver parameters
	Start recording
	Stop recording
o	ADCS
	Change attitude mode
	Desaturate RCS
o	COMM
	Get telemetry
	Upload mission script
	Download science data
•	Subsystem behavior
o	Geometry & mass
	Important for ADCS
	All subsystems are modelled as blocks
o	Power subsystem
	Current/voltage/power draw simulation
	Thermal dissipation
o	Thermal subsystem
	Use nodal model
o	OBDH (take runtime from OPS_SAT)
o	COMM (include ground station visibility)

Mission Scenarios
•	Save/Resume logic
o	Upon creation, create and save mission instance in the DB
o	Create unique mission hash/create database object
o	On each step, update mission simulation object

TODO:
Mission scenarios
•	Create a few example mission scenarios
•	Take examples from VEGA MiniSim
o	Imager missions
	take photo on the ground
	take photo of celestial object
	take photo of another satellite
o	SDR missions
	AIS intercept
	ADS-B intercept
	“Other satellite” transmission intercept

Environment & satellite simulation
•	Add night-day functionality.
•	Add irradiation conditions (beta angle, thermals, etc)
•	Add proper orbit simulation?
•	Add ADCS functionality (how to use quaternions??)
•	Share mission functionality (add screen to enter email to get mission url with hash) 
