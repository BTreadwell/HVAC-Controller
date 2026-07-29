# HVAC Controller

Implementation of a virtual PLC for a single-zone HVAC controller. The controller features:
- Hysteresis based staging logic
- Fan overrun timing
- Fail-safe fault handling

## Implementation Details

The HVAC unit consists of a heating component, cooling component, fan, and alarm/fault indicator along with a temperature sensor.

It has 4 modes of operation: heating, cooling, off, and fault.

For a specified set point, dead band, and safe temperature range:
- heating will turn on when the temperature is below setPoint - deadBand and turn off when the setPoint is reached
- cooling will turn on when the temperature is above setPoint + deadBand and turn off when the setPoint is reached
- the fault state will activate if the temperature ever falls outside the safe range

The fan will turn on if either heating or cooling is active and will stay on for 30 seconds after heating/cooling turns off

## Tools Used
Program was developed using the Autonomy Edge platform with the PLC logic written in Structured text. 
An orchestrator managed and ran a vPLC in a docker container on a linux laptop. 
The pymodbus library was used to simulate a tcp/ip modbus client.
The implementation was tested by connecting a virtual modbus client device created using the pymodbus library.


## File Descriptions

- PLC/HVAC_Controller.st contains the PLC logic
- hvac_vmodbus.py contains the code for the virtual modbus
- modbus_coil_watch.py contains code for monitoring the coil/register status
- hvac_test.py contains a unit test suite to validate the implementation according to specifications.
