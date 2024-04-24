from evennia import TICKER_HANDLER as ticker
import evennia
import clingo
import threading
import time
from evennia import AttributeProperty
from evennia.typeclasses.attributes import NAttributeProperty
from typeclasses.objects import Object

class Hardcodable(Object, Simulatable):
    program_slots = AttributeProperty(default=4)
    loaded_programs = NAttributeProperty(default={})
    running_programs = NAttributeProperty(default={})
    clock_speed = AttributeProperty(default=1)
    logs = NAttributeProperty(default=[])

    def is_loaded(self, program_key):
        if program_key in self.loaded_programs:
            return self.loaded_programs[program_key]
        else:
            return False
            

    def is_running(self, program_key):
        if program_key in self.running_programs:
            return self.running_programs[program_key]
        else:
            return False

    def load_program(self, program_key):
        possible_program = self.search(program_key)
        if possible_program != None:
            self.loaded_programs[program_key] = possible_program
            return True
        else:
            return False

    def run_program(self, program_key):
        possible_program = self.is_loaded(program_key)

        if not possible_program:
            return False
        else:
            self.running_programs[program_key] = possible_program
            return True

    def kill_program(self, program_key):
        possible_program = self.is_running(program_key)

        if possible_program:
            del self.running_programs[program_key]
        pass

        # If it's NOT in running_programs, it's def dead?
        return True

    def unload_program(self, program_key):
        possible_program = self.is_loaded(program_key)
        if possible_program:
            del self.loaded_programs[program_key]

        # If it's NOT in loaded_programs, it's def not loaded?
        return True

    def edit_program(self, program_key):
        pass

    def list_all_programs(self):
        # handle this intelligently.
        return []

    def show_specs(self):
        # show a single string summarizing the information. A prompt.
        pass

    # This is after we ran the simulation, internally Simulatable will call this
    def receive_output_terms(self, model):
        pass

    def parse_clingo_symbol(self, clingo_symbol):
        # This is where we will look for actual commands to fire.
        pass

    def view_data_stream(self):
        # This prints out the clingo symbols defining the snapshot of information the Hardcodable has access to
        pass

    def update_data_stream(self, data_dict):
        # This stores the latest snapshot of information
        pass

    def execute_command(self, command):
        # this attempts to execute a real evennia mud command as the player
        pass

class HardcodeProgram(Object):
    hardcode_content = AttributeProperty(default="")

    def to_fact(self):
        pass

    def edit_program(self):
        pass

    def save_program(self):
        pass

    def test_program(self):
        pass
