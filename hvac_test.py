import unittest
import time
from pymodbus.client import ModbusTcpClient
from dotenv import load_dotenv
import os

FAULT = 3
FAN = 2
COOL = 1
HEAT = 0

load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
DEVICE_ID = int(os.getenv("DEVICE_ID"))

def _get_count_from_fahrenheit(temp: float) -> int:
    counts = int(temp * (27648 - 5530) / 100.0) + 5530
    return counts

class TestHvac(unittest.TestCase):
    def setUp(self):
        self.client = ModbusTcpClient(host=HOST, port=PORT)
        self.assertTrue(self.client.connect())

    def tearDown(self):
        self.client.write_register(address=0, value=_get_count_from_fahrenheit(69))
        time.sleep(1)
        self.client.write_register(address=0, value=_get_count_from_fahrenheit(71))
        time.sleep(31)
        bits = self.client.read_coils(address=0, count=4).bits
        [self.assertFalse(bit) for bit in bits]

    def test_fault_state_activates_hot(self):
        hot_temp = _get_count_from_fahrenheit(temp=100)
        self.client.write_register(address=0, value=hot_temp)
        time.sleep(1)
        fault_state = self.client.read_coils(address=0, count=4).bits[FAULT]
        self.assertTrue(fault_state)

    def test_fault_state_activates_cold(self):
        cold_temp = _get_count_from_fahrenheit(temp=30)
        self.client.write_register(address=0, value=cold_temp)
        time.sleep(1)
        fault_state = self.client.read_coils(address=0, count=4).bits[FAULT]
        self.assertTrue(fault_state)

    def test_heating_activates(self):
        temp = _get_count_from_fahrenheit(temp=67)
        self.client.write_register(address=0, value=temp)
        time.sleep(1)
        bits = self.client.read_coils(address=0, count=4).bits
        self.assertTrue(bits[HEAT] and bits[FAN])
        self.assertFalse(bits[COOL] or bits[FAULT])


    def test_cooling_activates(self):
        temp = _get_count_from_fahrenheit(temp=73)
        self.client.write_register(address=0, value=temp)
        time.sleep(1)
        bits = self.client.read_coils(address=0, count=4).bits
        self.assertFalse(bits[HEAT] and bits[FAULT])
        self.assertTrue(bits[COOL] or bits[FAN])

    def test_fan_off_delay(self):
        # start heat
        temp = _get_count_from_fahrenheit(temp=67)
        self.client.write_register(address=0, value=temp)
        time.sleep(1)
        bits = self.client.read_coils(address=0, count=4).bits
        # verify state
        self.assertTrue(bits[HEAT] and bits[FAN])
        self.assertFalse(bits[COOL] or bits[FAULT])

        # end heat need
        neutral_temp = _get_count_from_fahrenheit(temp=71)
        self.client.write_register(address=0, value=neutral_temp)
        time.sleep(1)
        bits = self.client.read_coils(address=0, count=4).bits
        self.assertTrue(bits[FAN])
        self.assertFalse(bits[COOL] or bits[FAULT] or bits[HEAT])
        time.sleep(30)
        bits = self.client.read_coils(address=0, count=4).bits
        [self.assertFalse(bit) for bit in bits]

def runtests():
    unittest.main()

if __name__ == "__main__":
    client = ModbusTcpClient(host=HOST, port=PORT)
    client.connect()

    while True:
        tmp = int(input("temp: "))
        counts = _get_count_from_fahrenheit(temp=tmp)
        print(f"converted, that is: {counts}")
        print("sending")
        client.write_register(address=0, value=tmp)
        bits = client.read_coils(address=0, count=4).bits
        print('bits: ' + str(bits))
        read_tmp = client.read_holding_registers(address=0, count=1).registers
        print('regs: ' + str(read_tmp))




