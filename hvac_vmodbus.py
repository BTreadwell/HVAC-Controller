"""
Simple Modbus TCP slave (server) simulator using pymodbus
"""

from pymodbus.simulator import SimData, SimDevice, DataType
from pymodbus.server import StartTcpServer
from pymodbus import pymodbus_apply_logging_config
from dotenv import load_dotenv
import os

load_dotenv()

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT"))
DEVICE_ID = int(os.getenv("DEVICE_ID"))

pymodbus_apply_logging_config("DEBUG")

def main():
    # initialize coils, inputs, and registers
    coils = [SimData(0, count=4, values=False, datatype=DataType.BITS)]
    discrete_inputs = [SimData(0, count=8, values=False, datatype=DataType.BITS)]
    holding_registers = [SimData(0, count=1, values=5530, datatype=DataType.INT16)]
    input_registers = [SimData(0, count=8, values=0, datatype=DataType.REGISTERS)]

    # The tuple order is (coils, discrete_inputs, holding_registers, input_registers)
    device = SimDevice(
        DEVICE_ID,
        simdata=(coils, discrete_inputs, holding_registers, input_registers),
    )

    print(f"Starting Modbus TCP slave on {HOST}:{PORT} (device_id={DEVICE_ID}) ...")
    print(f"coils: 0 = heat; 1 = cool; 2 = fan; 3 = alarm")
    print(f"holding registers: 0 = temp_sensor, int16")

    StartTcpServer(context=device, address=(HOST, PORT))

if __name__ == "__main__":
    main()
