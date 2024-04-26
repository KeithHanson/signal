from prolog.simulatable import Simulatable

from evennia.utils import create
from evennia.utils.test_resources import EvenniaTest, EvenniaCommandTest
from unittest.mock import patch, MagicMock
from typeclasses.objects import Object
from prolog.hardcodable import Hardcodable, HardcodeProgram

import random
import time

class MyHardcodeComputer(Hardcodable):
    pass

class MySensor:
    def to_fact(self):
        random_int = random.randint(1, 100)
        return f"fake_sensor(10)."


class TestHardcodeSystem(EvenniaCommandTest):
    def setUp(self):
        super().setUp()

        
        self.pc = create.create_object( MyHardcodeComputer, key="pc" )

        self.hc_program = create.create_object( HardcodeProgram, key="smoke_test" )
        self.hc_program.hardcode_content = "hello(world). #show hello/1."

        self.hc_program.move_to(self.pc)

    def test_smoke_test(self):
        self.assertEqual(isinstance(self.pc, Hardcodable), True) 
        self.assertEqual(self.pc.program_slots, 4)
        self.assertEqual(self.pc.clock_speed, 1)
        self.assertEqual(self.pc.logs, [])
        self.assertEqual(self.items_length(self.pc.running_programs), 0)
        self.assertEqual(self.items_length(self.pc.loaded_programs), 0)

        self.assertEqual(self.hc_program.hardcode_content,"hello(world). #show hello/1." )

    def items_length(self, incoming_dict):
        return len(list(incoming_dict.items()))

    def test_program_load_and_run(self):
        #shouldn't fail
        self.assertEqual(self.pc.load_program("smoke_test"), True)

        self.assertEqual(self.items_length(self.pc.loaded_programs), 1)

        self.assertEqual(self.pc.run_program("smoke_test"), True)

        self.assertEqual(self.items_length(self.pc.running_programs), 1)

        self.assertEqual(self.pc.kill_program("smoke_test"), True)

        self.assertEqual(self.items_length(self.pc.running_programs), 0)

        self.assertEqual(self.pc.unload_program("smoke_test"), True)

        self.assertEqual(self.items_length(self.pc.loaded_programs), 0)

        self.assertEqual(self.pc.run_program("smoke_test"), False)

        self.assertEqual(self.items_length(self.pc.running_programs), 0)

    def test_add_remove_sensors(self):
        my_sensor = MySensor()

        self.pc.add_sensor(my_sensor)
        self.pc.remove_sensor(my_sensor)

    def test_data_stream(self):
        my_sensor = MySensor()

        self.pc.add_sensor(my_sensor)
        self.pc.view_data_stream()

        self.assertEqual(self.pc.view_data_stream(), "fake_sensor(10).")

    def test_program_run_and_check_output(self):
        self.hc_program.hardcode_content = "hello(world). #show hello/1."
        self.pc.load_program("smoke_test")
        self.pc.run_program("smoke_test")
        self.pc.debugging = True

        time.sleep(1)

        self.assertEqual(len(self.pc.logs) > 0, True)

        logs = "\n".join(self.pc.logs)

        self.assertEqual("Program loaded: smoke_test" in logs, True)
        self.assertEqual("Adding to running programs: smoke_test" in logs, True) 
        self.assertEqual("Execution loop complete." in logs, True)
        self.assertEqual("DEBUG: Received truth from last loop:" in logs, True)


    def test_program_run_and_parsing_of_command(self):
        self.hc_program.hardcode_content = "hello(world). #show hello/1. command(look). #show command/1."
        self.pc.load_program("smoke_test")
        self.pc.run_program("smoke_test")
        self.pc.debugging = True

        time.sleep(1)

        self.assertEqual(len(self.pc.logs) > 0, True)

        logs = "\n".join(self.pc.logs)
        self.assertEqual("MATCHED COMMAND:" in logs, True)
