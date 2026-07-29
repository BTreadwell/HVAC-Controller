"""
Poll hvac_vmodbus coils + holding registers for debugging
"""

import time
from pymodbus.client import ModbusTcpClient
from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
DEVICE_ID = int(os.getenv("DEVICE_ID"))
POLL_INTERVAL = 0.2

def main():
    client = ModbusTcpClient(HOST, port=PORT)
    client.connect()

    print(f"Watching coils 0-3 on {HOST}:{PORT} (device_id={DEVICE_ID})")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            coil_values = client.read_coils(0, count=4, device_id=DEVICE_ID)
            if coil_values.isError():
                print(f"Error reading coils: {coil_values}")
            else:
                bits = coil_values.bits[:4]
                display = " ".join("1" if b else "0" for b in bits)
                print(f"\rCoils: {display}", end="", flush=True)
            print("", flush=True)
            # read 2 regs bc temp is 16 bit int
            temp_regs = client.read_holding_registers(address=0, count=1).registers
            temp_value = client.convert_from_registers(temp_regs, data_type=client.DATATYPE.INT16)
            print(f"Temperature: {temp_value}", flush=True)

            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        client.close()

if __name__ == "__main__":
    main()
