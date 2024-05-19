from evennia.contrib.base_systems.unixcommand import UnixCommand
from evennia.contrib.base_systems.unixcommand.unixcommand import HelpAction, UnixCommandParser
from commands.command import Command
from evennia import CmdSet
from evennia.utils import create
import argparse

class CoreUnixCommand(UnixCommand):
    def at_post_cmd(self):
        if hasattr(self.caller, "update_status"):
            self.caller.update_status()

class CmdCoreLs(CoreUnixCommand):

    '''
    List all objects available to your core. Mostly used to list your HardcodePrograms.

    Examples:
        ls
        ls -l
    '''

    key = "ls"
    help_category = "Core Binaries"

    def init_parser(self):
        self.parser.add_argument("-l", "--long", 
            help="List more detail of each item", action="store_true")

    def func(self):
        long = self.opts.long

        item_string = ', '.join( [ item.key for item in self.caller.contents] )

        if self.opts.long:
            # show items in table
            self.caller.msg("-l not implemented yet.")

        contents_length = len(self.caller.contents)
        self.caller.msg(f"{contents_length} Objects Available\n{item_string}")

class CmdHardcodeCompiler(CoreUnixCommand):
    """
    Hardcode Compiler. Allows you to test a program.

    Usage:
    hcc program
    """

    key = "hcc"
    aliases = []
    locks = "cmd:false()"
    help_category = "Core Binaries"

    def init_parser(self):
        self.parser.add_argument("name",
                help="name of the program to test")

    def func(self):
        caller = self.caller
        target = caller.search(self.opts.name)

        if not target:
            return

        if hasattr(target, "hardcode_content"):
            target.test_program(caller)

class CmdCoreReload(CoreUnixCommand):
    """
    Restarts and resets your core's simulation loop.

    Usage:
       restart 
    """

    key = "restart"
    aliases = []
    locks = "cmd:false()"
    help_category = "Core Binaries"

    def func(self):
        caller = self.caller
        caller.reload()
        caller.msg("Core simulator restarted.")
                
class CmdCoreLoadProgram(CoreUnixCommand):
    """
    Load a program into your aiCore, by it's key.
    This will place the program into the inventory of the aiCore and will take up one of its slots.
    You can get it back by unloading it.

    Usage:
       load name 
    """

    key = "load"
    aliases = []
    locks = "cmd:false()"
    help_category = "Core Binaries"

    def init_parser(self):
        self.parser.add_argument("name",
                help="name of the program to load")

    def func(self):
        caller = self.caller

        try:
            program = caller.search(self.opts.name)
        except:
            pass

        if not program:
            return

        if program:
            if caller.load_program(self.opts.name):
                caller.msg(f"Program ready to |grun.")
            else:
                caller.msg(f"|rFailed to load the program.")

class CmdCoreUnloadProgram(CoreUnixCommand):
    """
    Unload a program from your Core, by it's name. 
    This will free up a slot.

    Usage:
       unload name 
    """

    key = "unload"
    aliases = []
    locks = "cmd:false()"
    help_category = "Core Binaries"

    def init_parser(self):
        self.parser.add_argument("name",
                help="name of the program to load")

    def func(self):
        caller = self.caller
        try:
            program = caller.search(self.opts.name)
        except: 
            pass

        if not program:
            caller.msg(f"Cannot find program: {self.opts.name}")

        if program:
            if caller.unload_program(self.opts.name):
                caller.msg(f"A slot has been freed in the core.")
            else:
                caller.msg(f"Core failed to unload the program.")

class CmdCoreEditProgram(CoreUnixCommand):
    """
    Edit a program, by it's name. If it does not exist, it will be created.
    This will enter an editor. Type :h once inside for help.

    Usage:
       vim name 
    """

    key = "vim"
    aliases = []
    locks = "cmd:false()"
    help_category = "Core Binaries"

    def init_parser(self):
        "Add the arguments to the parser."
        # 'self.parser' inherits `argparse.ArgumentParser`
        self.parser.add_argument("name",
                help="name of the program to edit")

    def func(self):
        caller = self.caller

        try:
            program = caller.search(self.opts.name)
        except: 
            pass

        if not program:
            program = create.create_object( "prolog.hardcodable.HardcodeProgram", key=self.opts.name, location=caller )

        if program:
            program.edit_program(caller)

class CmdCoreRunProgram(CoreUnixCommand):
    """
    Run a program that has been loaded into your aiCore, by it's key.
    This will cause your program to be added to the simulation loop 
    with all other running programs.

    Usage:
       run name 
    """

    key = "run"
    aliases = []
    locks = "cmd:false()"
    help_category = "Core Binaries"

    def init_parser(self):
        "Add the arguments to the parser."
        # 'self.parser' inherits `argparse.ArgumentParser`
        self.parser.add_argument("name",
                help="name of the program to load")

    def func(self):
        caller = self.caller

        try:
            program = caller.search(self.opts.name)
        except: 
            pass

        if not program:
            caller.msg(f"Cannot find program: {self.opts.name}")

        if program:
            if caller.run_program(self.opts.name):
                caller.msg(f"The core is now running: {self.opts.name}.")
            else:
                caller.msg(f"Core failed to run the program. Is it loaded?")

class CmdCoreKillProgram(CoreUnixCommand):
    """
    Kill a program that is running on your Core, by it's name.
    This will remove that program from your simulation loop.

    Usage:
       kill name 
    """

    key = "kill"
    aliases = []
    locks = "cmd:false()"
    help_category = "Core Binaries"

    def init_parser(self):
        self.parser.add_argument("name",
                help="name of the program to kill")

    def func(self):
        caller = self.caller

        try:
            program = caller.search(self.opts.name)
        except: 
            pass

        if not program:
            caller.msg(f"Cannot find program: {self.opts.name}")

        if program:
            if caller.kill_program(self.opts.name):
                caller.msg(f"The core killed: {self.opts.name}.")
            else:
                caller.msg(f"Core failed to kill the program. Is it running?")

class CmdCoreShowLoadedPrograms(CoreUnixCommand):
    """
    Show the loaded programs.

    Usage:
       loaded 
    """

    key = "loaded"
    aliases = []
    locks = "cmd:false()"
    help_category = "Core Binaries"

    def func(self):
        caller = self.caller

        caller.msg("List of HardcodePrograms:")
        caller.msg(", ".join(program for program in caller.loaded_programs))

class CmdCoreShowRunningPrograms(CoreUnixCommand):
    """
    Show the running programs.

    Usage:
       ps 
    """

    key = "ps"
    aliases = []
    locks = "cmd:false()"
    help_category = "Core Binaries"

    def func(self):
        caller = self.caller

        caller.msg("Running Programs:")
        caller.msg(", ".join(program for program in caller.running_programs))

class CmdCoreToggleNoisy(CoreUnixCommand):
    """
    Have the core report every simulation loops' output.

    Usage:
       noisy 
    """

    key = "noisy"
    aliases = []
    locks = "cmd:false()"
    help_category = "Core Binaries"

    def func(self):
        caller = self.caller
        caller.noisy = not caller.noisy


class CmdCoreShowDataStream(CoreUnixCommand):
    """
    View a snapshot of the sensor data being fed to your program.
    These are the facts that allow you to make decisions within your program.

    Usage:
       datastream 
    """

    key = "datastream"
    aliases = []
    locks = "cmd:false()"
    help_category = "Core Binaries"

    def func(self):
        caller = self.caller
        caller.msg("|yDatastream of Connected Sensors:")
        caller.msg(f"|b{caller.view_data_stream()}")

class CmdCoreShowLogs(CoreUnixCommand):
    """
    View a the output from loops of your programs.

    Usage:
       logs 
    """

    key = "logs"
    aliases = []
    locks = "cmd:false()"
    help_category = "Core Binaries"

    def func(self):
        caller = self.caller
        caller.msg("\n".join(caller.logs[-10:]))

class CmdCoreShowLastError(CoreUnixCommand):
    """
    View the output of the last error that stopped your core's simulation.
    Use --clear to clear the error state.

    Usage:
       error 
       error --clear
    """

    key = "error"
    aliases = []
    locks = "cmd:false()"
    help_category = "Core Binaries"

    def init_parser(self):
        self.parser.add_argument("--clear", action="store_true",
                help="Clears the error state of the simulation after showing the error.")

    def func(self):
        caller = self.caller

        caller.msg("|yLast Core Simulation Loop Error Before Termination:")
        caller.msg(caller.last_error)

        if self.opts.clear:
            caller.clear_failure()
            caller.last_error = None
            caller.failure = False
            caller.reload()

            caller.msg("Core simulation loop reloaded.")

class CmdCoreShowProgram(CoreUnixCommand):
    """
    Show the entire program the core will run in the loop.

    Usage:
        sim
    """

    key = "sim"
    aliases = []
    locks = "cmd:false()"
    help_category = "Core Binaries"

    def func(self):
        caller = self.caller

        caller.msg("|yCore simulation loop:")
        caller.msg(f"|b{caller.program()}")

class CmdCoreLinkTo(CoreUnixCommand):
    """
    Display the linkages when no argument is given. 
    Link your core to another subsystem. 
    If you provide two arguments, it will link that system to 
    the other system.

    Usage:
        link subsystem --to other_subsystem

    Example:
        link
        link reactor
        link reactor --to battery
        link battery --to radar
        link battery --to engine
    """
    key = "link"
    aliases = []
    locks = "cmd:false()"
    help_category = "Core Binaries"

    def init_parser(self):
        self.parser.add_argument("subsystem",
                help="the name of the subsystem to link to the core, or the subsystem to link from when provided a --to")

        self.parser.add_argument("-t", "--to",
                help="the subsystem to link the first subsystem to")

    def func(self):
        caller = self.caller
        subsystem = self.opts.subsystem
        other_subsystem = self.opts.to

        if not self.args:
            caller.msg("|rError. |yMust provide at least |gone subsystem |yto link the |bcore|y to, or |gtwo subsystems|n to link together.")

        if not other_subsystem:
            target = caller.search(subsystem)

            if caller.link_to(target):
                caller.msg(f"Core linked to {subsystem} successfully.")

        else:
            if not subsystem:
                return

            if not other_subsystem:
                return

            if subsystem.link_to(other_subsystem):
                caller.msg(f"{subsystem} linked to {other_subsystem} successfully")

class CmdCoreRegistry(CoreUnixCommand):
    """
    Set a register slot to a fact. Use --toggle to turn it on or off. Use registry slot to unset a register.

    Usage:
        registry slot fact --toggle

    Example:
        Set the register slot 0 to low speed, register 1 to faster, toggle the faster speed off. 
        Later, toggle low speed off, and high speed on. 
        Later, delete slot 0 register.

        registry 0 "max_velocity(1)."
        registry 1 "max_velocity(10)."
        registry 1 --toggle

        registry 0 --toggle 
        registry 1 --toggle

        registry 0
    """
    key = "registry"
    aliases = []
    locks = "cmd:false()"
    help_category = "Core Binaries"

    def init_parser(self):
        self.parser.add_argument("slot", help="Set which slot for this command. Starts at 0.")
        self.parser.add_argument("--fact", "-f", required=False, help="Set the fact to set in the register. There is no error checking, and it will be injected into the simulation as soon as it is set.")
        self.parser.add_argument("--toggle", action="store_true", help="Ignores anything else and toggles the slot setting.")

    def func(self):
        if self.opts.toggle:
            self.caller.toggle_registry(int(self.opts.slot))
            self.caller.msg(f"Registry slot {self.opts.slot} toggled.")
            return True

        if self.opts.slot and self.opts.fact:
            self.caller.set_registry(int(self.opts.slot), self.opts.fact)
            self.caller.msg(f"Registry slot {self.opts.slot} fact set to: '{self.opts.fact}'")
            return True

        if self.opts.slot and not self.opts.fact:
            self.caller.set_registry(int(self.opts.slot), None)
            self.caller.msg(f"Registry slot {self.opts.slot} cleared.")
            return True

class CmdCoreShowRegistries(CoreUnixCommand):
    """
    Show all registry facts and toggles.
    """

    key = "registries"
    aliases = []
    locks = "cmd:false()"
    help_category = "Core Binaries"

    def func(self):
        caller = self.caller
        self.caller.msg(caller.show_registry())

class CoreCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdHardcodeCompiler)
        self.add(CmdCoreReload)
        self.add(CmdCoreLoadProgram)
        self.add(CmdCoreUnloadProgram)
        self.add(CmdCoreRunProgram)
        self.add(CmdCoreKillProgram)
        self.add(CmdCoreShowDataStream)
        self.add(CmdCoreShowLogs)
        self.add(CmdCoreShowLastError)
        self.add(CmdCoreShowLoadedPrograms)
        self.add(CmdCoreShowRunningPrograms)
        self.add(CmdCoreToggleNoisy)
        self.add(CmdCoreLinkTo)
        self.add(CmdCoreShowProgram)
        self.add(CmdCoreLs)
        self.add(CmdCoreEditProgram)
        self.add(CmdCoreRegistry)
        self.add(CmdCoreShowRegistries)
