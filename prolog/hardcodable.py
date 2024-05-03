from evennia import TICKER_HANDLER as ticker
import evennia
import clingo
import threading
import time
from evennia import AttributeProperty
from evennia.typeclasses.attributes import NAttributeProperty
from typeclasses.objects import Object
from prolog.simulatable import Simulatable
import re
from evennia.utils.eveditor import EvEditor
import traceback



class Hardcodable(Object, Simulatable):
    program_slots = AttributeProperty(default=4)

    loaded_programs = NAttributeProperty(default={})

    running_programs = NAttributeProperty(default={})

    clock_speed = AttributeProperty(default=1)

    logs = NAttributeProperty(default=[])
    
    sensors = NAttributeProperty(default=[])

    debugging = NAttributeProperty(default=False)

    noisy = False

    def to_fact(self):
        return ""

    def at_init(self):
        self.track(self)
        return True

    def program(self):
        # Gather terms from all the sensors, these are our facts.
        fact_section = "\n".join([ sensor.to_fact() for sensor in self.sensors])
        # Inject the running programs beneath the sensor data
        program_section = "\n".join([ program.to_fact() for _, program in self.running_programs.items()])

        output = "%Facts from sensors.\n" + fact_section + "\n\n%User Hardcode\n" + program_section

        if self.debugging:
            self.logs.append("DEBUG: Full program and sensor facts:")
            self.logs.append(output)

        return output

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
            self.logs.append(f"Program loaded: {program_key}")
            return True
        else:
            return False
    
    def reload(self):
        self.ignore(self)
        self.track(self)
        return True

    def run_program(self, program_key):
        possible_program = self.is_loaded(program_key)

        if not possible_program:
            return False
        else:
            self.running_programs[program_key] = possible_program

            self.logs.append(f"Adding to running programs: {program_key}")

            self.reload()

            return True

    def kill_program(self, program_key):
        possible_program = self.is_running(program_key)

        if possible_program:
            del self.running_programs[program_key]
            self.logs.append(f"Killed running program: {program_key}")
        pass

        # If it's NOT in running_programs, it's def dead?
        return True

    def unload_program(self, program_key):
        possible_program = self.is_loaded(program_key)
        if possible_program:
            self.kill_program(program_key)
            del self.loaded_programs[program_key]

        # If it's NOT in loaded_programs, it's def not loaded?
        self.logs.append(f"Program unloaded: {program_key}")
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
    def update(self, model):
        self.logs.append(f"Execution loop complete.")
        self.parse_clingo_symbols(model.symbols(shown=True))

    def parse_clingo_symbols(self, clingo_symbols):
        # This is where we will look for actual commands to fire.
        if self.debugging: 
            self.logs.append("Sensor data:")
            self.logs.append(self.view_data_stream())

        self.logs.append(f"Received output from last loop: ")
        self.logs.append(f"{clingo_symbols}")
        if self.noisy:
            self.location.msg_contents(f"The core bleeps and bloops noisily.")
            self.location.msg_contents(f"Simulation Truths: {clingo_symbols}")


        for symbol in clingo_symbols:
            pattern = re.compile(r'command\("(.*?)"\)')
            match_object = re.match(pattern, str(symbol))

            if match_object:
                if self.debugging:
                    self.logs.append("MATCHED COMMAND: ")
                self.logs.append("Executing command: " + match_object.group(1))
               #self.logs.append(f"Output from command: {self.execute_command(match_object.group(1))}")
                self.execute_command(match_object.group(1))    

    def add_sensor(self, sensor_obj):
        if not sensor_obj in self.sensors:
            self.sensors.append(sensor_obj)

        self.logs.append(f"Sensor connected: {sensor_obj}")
        return True

    def remove_sensor(self, sensor_obj):
        if sensor_obj in self.sensors:
            self.sensors.remove(sensor_obj)

        self.logs.append(f"Sensor disconnected: {sensor_obj}")
        return True

    def view_data_stream(self):
        # This prints out the clingo symbols defining the snapshot of information the Hardcodable has access to
        return "\n".join([sensor.to_fact() for sensor in self.sensors])

    def execute_command(self, command):
        # this attempts to execute a real evennia mud command as the player
        pass

class HardcodeProgram(Object):
    hardcode_content = AttributeProperty(default="")

    def __str__(self):
        return f"{self.key} \n\n {self.hardcode_content}"


    def to_fact(self):
        return self.hardcode_content

    def editor_load(self, caller):
        return self.hardcode_content 

    def editor_save(self, caller, buffer):
        self.hardcode_content = buffer.strip()
        self.save()

    def editor_quit(self, caller):
        caller.msg("You watch as the program's circuits shift to your whims.")

    def edit_program(self, caller):
        EvEditor(caller, loadfunc=self.editor_load, savefunc=self.editor_save, quitfunc=self.editor_quit, key=self.key)

    def test_program(self, caller):
        try:
            ctl = clingo.Control()
            core = caller.search("core")

            if not core:
                caller.msg("A core must be nearby to test this program.")
                return False

            program = "\n".join([ sensor.to_fact() for sensor in core.sensors]) + self.hardcode_content

            ctl.add('base', [], program)
            ctl.ground([("base", [])])
            
            def on_clingo_model(model):
                caller.msg("|gThe program beeps softly to get your attention. The test is complete.")
                caller.msg(f"|b{program}")
                for symbol in model.symbols(shown=True):
                    caller.msg(f"|y{symbol}")
                
            ctl.solve(on_model=on_clingo_model)
            ctl.cleanup()
        except RuntimeError as e:
            caller.msg(e.__cause__)
            caller.msg(traceback.format_exc())
