from prolog.simulatable import Simulatable

from evennia.utils import create
from evennia.utils.test_resources import EvenniaTest, EvenniaCommandTest
from unittest.mock import patch, MagicMock
from typeclasses.objects import Object
from prolog.hardcodable import Hardcodable, HardcodeProgram


class MyHardcodeComputer(Hardcodable):
    pass

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

    def test_program_load(self):
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
