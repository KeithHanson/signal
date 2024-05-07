"""
Object

The Object is the "naked" base class for things in the game world.

Note that the default Character, Room and Exit does not inherit from
this Object, but from their respective default implementations in the
evennia library. If you want to use this class as a parent to change
the other types, you can do so by adding this as a multiple
inheritance.

"""

from evennia.objects.objects import DefaultObject, DefaultRoom

from evennia import CmdSet, AttributeProperty
from evennia.typeclasses.attributes import NAttributeProperty
from evennia import TICKER_HANDLER as tickerhandler
import evennia
from evennia.utils import create

from evennia.utils import utils

from django.conf import settings
COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)

from commands.command import Command

from prolog.simulatable import Simulatable


class Vehicle:
    pass

class DefaultRadar:
    pass

# Pearl clutch! I know, I re-opened the class. I'm a dirty rubyist at heart. 
DefaultRoom.newtonian_data = NAttributeProperty(default={"x": 0, "y": 0, "Fx": 0, "Fy": 0, "Vx": 0, "Vy": 0})

class ObjectParent:
    """
    This is a mixin that can be used to override *all* entities inheriting at
    some distance from DefaultObject (Objects, Exits, Characters and Rooms).

    Just add any method that exists on `DefaultObject` to this class. If one
    of the derived classes has itself defined that same hook already, that will
    take precedence.

    """
    newtonian_data = NAttributeProperty(default={"x": 0, "y": 0, "Fx": 0, "Fy": 0, "Vx": 0, "Vy": 0, "wasMoving": False})


class Object(ObjectParent, DefaultObject):
    """
    This is the root typeclass object, implementing an in-game Evennia
    game object, such as having a location, being able to be
    manipulated or looked at, etc. If you create a new typeclass, it
    must always inherit from this object (or any of the other objects
    in this file, since they all actually inherit from BaseObject, as
    seen in src.object.objects).

    The BaseObject class implements several hooks tying into the game
    engine. By re-implementing these hooks you can control the
    system. You should never need to re-implement special Python
    methods, such as __init__ and especially never __getattribute__ and
    __setattr__ since these are used heavily by the typeclass system
    of Evennia and messing with them might well break things for you.


    * Base properties defined/available on all Objects

     key (string) - name of object
     name (string)- same as key
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation

     account (Account) - controlling account (if any, only set together with
                       sessid below)
     sessid (int, read-only) - session id (if any, only set together with
                       account above). Use `sessions` handler to get the
                       Sessions directly.
     location (Object) - current location. Is None if this is a room
     home (Object) - safety start-location
     has_account (bool, read-only)- will only return *connected* accounts
     contents (list of Objects, read-only) - returns all objects inside this
                       object (including exits)
     exits (list of Objects, read-only) - returns all exits from this
                       object, if any
     destination (Object) - only set if this object is an exit.
     is_superuser (bool, read-only) - True/False if this user is a superuser

    * Handlers available

     aliases - alias-handler: use aliases.add/remove/get() to use.
     permissions - permission-handler: use permissions.add/remove() to
                   add/remove new perms.
     locks - lock-handler: use locks.add() to add new lock strings
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().
     sessions - sessions-handler. Get Sessions connected to this
                object with sessions.get()
     attributes - attribute-handler. Use attributes.add/remove/get.
     db - attribute-handler: Shortcut for attribute-handler. Store/retrieve
            database attributes using self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create
            a database entry when storing data

    * Helper methods (see src.objects.objects.py for full headers)

     search(ostring, global_search=False, attribute_name=None,
             use_nicks=False, location=None, ignore_errors=False, account=False)
     execute_cmd(raw_string)
     msg(text=None, **kwargs)
     msg_contents(message, exclude=None, from_obj=None, **kwargs)
     move_to(destination, quiet=False, emit_to_obj=None, use_destination=True)
     copy(new_key=None)
     delete()
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False)
     check_permstring(permstring)

    * Hooks (these are class methods, so args should start with self):

     basetype_setup()     - only called once, used for behind-the-scenes
                            setup. Normally not modified.
     basetype_posthook_setup() - customization in basetype, after the object
                            has been created; Normally not modified.

     at_object_creation() - only called once, when object is first created.
                            Object customizations go here.
     at_object_delete() - called just before deleting an object. If returning
                            False, deletion is aborted. Note that all objects
                            inside a deleted object are automatically moved
                            to their <home>, they don't need to be removed here.

     at_init()            - called whenever typeclass is cached from memory,
                            at least once every server restart/reload
     at_cmdset_get(**kwargs) - this is called just before the command handler
                            requests a cmdset from this object. The kwargs are
                            not normally used unless the cmdset is created
                            dynamically (see e.g. Exits).
     at_pre_puppet(account)- (account-controlled objects only) called just
                            before puppeting
     at_post_puppet()     - (account-controlled objects only) called just
                            after completing connection account<->object
     at_pre_unpuppet()    - (account-controlled objects only) called just
                            before un-puppeting
     at_post_unpuppet(account) - (account-controlled objects only) called just
                            after disconnecting account<->object link
     at_server_reload()   - called before server is reloaded
     at_server_shutdown() - called just before server is fully shut down

     at_access(result, accessing_obj, access_type) - called with the result
                            of a lock access check on this object. Return value
                            does not affect check result.

     at_pre_move(destination)             - called just before moving object
                        to the destination. If returns False, move is cancelled.
     announce_move_from(destination)         - called in old location, just
                        before move, if obj.move_to() has quiet=False
     announce_move_to(source_location)       - called in new location, just
                        after move, if obj.move_to() has quiet=False
     at_post_move(source_location)          - always called after a move has
                        been successfully performed.
     at_object_leave(obj, target_location)   - called when an object leaves
                        this object in any fashion
     at_object_receive(obj, source_location) - called when this object receives
                        another object

     at_traverse(traversing_object, source_loc) - (exit-objects only)
                              handles all moving across the exit, including
                              calling the other exit hooks. Use super() to retain
                              the default functionality.
     at_post_traverse(traversing_object, source_location) - (exit-objects only)
                              called just after a traversal has happened.
     at_failed_traverse(traversing_object)      - (exit-objects only) called if
                       traversal fails and property err_traverse is not defined.

     at_msg_receive(self, msg, from_obj=None, **kwargs) - called when a message
                             (via self.msg()) is sent to this obj.
                             If returns false, aborts send.
     at_msg_send(self, msg, to_obj=None, **kwargs) - called when this objects
                             sends a message to someone via self.msg().

     return_appearance(looker) - describes this object. Used by "look"
                                 command by default
     at_desc(looker=None)      - called by 'look' whenever the
                                 appearance is requested.
     at_get(getter)            - called after object has been picked up.
                                 Does not stop pickup.
     at_drop(dropper)          - called when this object has been dropped.
     at_say(speaker, message)  - by default, called if an object inside this
                                 object speaks

    """

    pass

class CmdBootstrapSpaceroom(Command):
    """
    Superuser command for creating a quick SpaceRoom -> Room w SpaceRoomDock -> Ship.

    Usage:
        bootstrap_spaceroom
    """
    key = "bootstrap_spaceroom"
    
    locks = "cmd::perm(Builder)"

    help_category = "Builder Utilities"

    def func(self):
        room1 = create.create_object( "objects.DefaultRoom", key="hangar")
        self.caller.move_to(room1)

        default_vehicle = create.create_object( "vehicles.base.DefaultSpaceShip", key="ship" )
        default_vehicle.move_to(room1)

        space_room = create.create_object( SpaceRoom, key="space_room" )

        dock = create.create_object( SpaceRoomDock, key="dock",  )
        dock.exit_room = space_room

        
        room1.newtonian_data["x"] = 20
        room1.newtonian_data["y"] = 20

        dock.move_to(room1)
        room1.move_to(space_room)

class CmdPilotVehicle(COMMAND_DEFAULT_CLASS):
    """
    Begin piloting a vehicle.

    Usage:
        pilot ship

    If you have the proper permissions, you will climb into the vehicle and can begin controlling it.
    """

    key = "pilot"
    aliases = ["get in", "drive", "fly"]
    locks = "cmd:all()"
    help_category = "Piloting"

    def func(self):
        caller = self.caller

        if not self.args:
            target = caller.location
            if not target:
                caller.msg("You are neither in a ship nor have provided a target ship to pilot!")
                return

            if hasattr(target, "at_pilot_enter"):
                target.at_pilot_enter(caller)
            else:
                caller.msg("You can't pilot this!")
        else:
            target = caller.search(self.args)
            if not target:
                return
            if hasattr(target, "at_pilot_enter"):
                target.at_pilot_enter(caller)
            else:
                caller.msg("Hm... can't pilot that.")


class CmdDisembarkVehicle(Command):
    """
    Exit the vehicle you are in.

    Usage:
        disembark

    Get out of the vehicle, exiting into the location of the vehicle itself.
    """

    key = "disembark"
    aliases = ["get out", "leave", "exit"]
    locks = "cmd:all()"
    help_category = "Piloting"

    def parse(self):
        pass

    def func(self):
        caller = self.caller
        ship = caller.location

        ship.at_pilot_exit(caller)

class CmdPowerOnVehicle(Command):
    """
    Power up the vehicle.

    Usage:
        power on

    """

    key = "power on"
    aliases = ["boot up", "boot", "turn on", "on"]
    locks = "cmd:all()"
    help_category = "Piloting"

    def func(self):
        caller = self.caller
        ship = self.caller.location
        ship.at_power_on()


class CmdPowerOffVehicle(Command):
    """
    Power off the vehicle.

    Usage:
        power off

    """

    key = "power off"
    aliases = ["shutdown", "shut off", "turn off", "off"]
    locks = "cmd:all()"
    help_category = "Piloting"

    def func(self):
        caller = self.caller
        ship = self.caller.location
        ship.at_power_off()

class CmdPilotLaunch(Command):
    """
    Launch the vehicle into space from a room with a dock.

    Usage:
        launch
    """

    key = "launch"
    
    locks = "cmd:all()"
    help_category = "Piloting"

    def func(self):
        caller = self.caller
        ship = self.caller.location

        dock = ship.location.search("dock")

        if dock:
            ship.newtonian_data["x"] = dock.location.newtonian_data["x"]
            ship.newtonian_data["y"] = dock.location.newtonian_data["y"]

            ship.move_to(dock.exit_room)
            ship.msg_contents("|cLaunch procedure initiated...")
            ship.msg_contents("|cLaunch procedure initiated... \t|g[OK]")
            ship.msg_contents("|cEnsuring lane clear...")
            ship.msg_contents("|cEnsuring lane clear... \t\t|g[OK]")
            ship.msg_contents("|gLaunch procedure complete.")

        else:
            if isinstance(ship.location, SpaceRoom):
                caller.msg("You are already in space!")
            else:
                caller.msg("Couldn't find a dock. Contact a builder!")

class CmdPilotDock(Command):
    """
    Dock the vehicle from space to a room with a dock.

    Usage:
        launch
    """

    key = "dock"
    
    locks = "cmd:all()"
    help_category = "Piloting"

    def func(self):
        caller = self.caller
        ship = self.caller.location
        if not str(ship) == "ship":
            caller.msg("Are you in a vehicle?")
            return False

        space_room = ship.location

        if not isinstance(space_room, SpaceRoom):
            caller.msg("Are you already docked?")
            return False
        
        potential_rooms_with_docks = space_room.get_contents_near_position(ship.newtonian_data["x"], ship.newtonian_data["y"])

        for room in potential_rooms_with_docks:
            dock = room.search("dock")    

            if dock:
                ship.newtonian_data["x"] = dock.location.newtonian_data["x"]
                ship.newtonian_data["y"] = dock.location.newtonian_data["y"]
                ship.newtonian_data["Fx"] = 0
                ship.newtonian_data["Fy"] = 0
                ship.newtonian_data["Vx"] = 0
                ship.newtonian_data["Vy"] = 0

                ship.move_to(dock.location)
                ship.msg_contents("|cDocking procedure initiated...")
                ship.msg_contents("|cDocking procedure initiated... \t|g[OK]")
                ship.msg_contents("|cReserving docking pad... \t\t|g")
                ship.msg_contents("|cReserving docking pad... \t|g[OK]")
                ship.msg_contents("|cTether beam connecting...")
                ship.msg_contents("|cTether beam connecting... \t|g[OK]")
                ship.msg_contents("|cAttaching Harness...")
                ship.msg_contents("|cAttaching Harness... \t\t|g[OK]")
                ship.newtonian_data["wasMoving"] = False
                return True

        ship.msg_contents("Ship could not find a dock.")
        return False

class CmdRadarPulse(Command):
    """
    Pulses the radar, allowing you to "see" around your ship.

    Usage:
       radar pulse 

    """

    key = "radar pulse"
    aliases = ["pulse"]
    locks = "cmd:all()"
    help_category = "Radar Subsystems"

    def func(self):
        caller = self.caller
        ship = self.caller.location
        room = ship.location
        
        if not isinstance(room, SpaceRoom):
            caller.msg("Pulsing your radar while docked is dangerous.")
        else:
            radar = caller.search("radar")
            if not radar:
                caller.msg("Do you have a radar installed?")
            else:
                radar.pulse(caller, room)

class CmdEngineThrust(Command):
    """
    Pulses the radar, allowing you to "see" around your ship.

    Usage:
       thrust n 
       thrust s
       thrust e
       thrust w
       thrust reset
       thrust emergency_stop
    """

    key = "thrust"

    locks = "cmd:all()"

    help_category = "Engine Subsystems"

    def parse(self):
        if self.args.strip() == "":
            self.target = None
        else:
            self.target = self.args.strip()
        pass

    def func(self):
        caller = self.caller

        ship = self.caller.location

        room = ship.location

        if not isinstance(room, SpaceRoom):
            caller.msg("|rError: Docked. Engine locked.")
        else:
            engine = caller.search("engine")
            if not engine:
                caller.msg("|rCritical Panic: No engine.")
            else:
                thrust_msg = "|GThrust applied."

                notify_failure = False

                if self.target == "n":
                    if engine.thrust_north():
                        ship.msg_contents(thrust_msg)
                    else:
                        notify_failure = True

                elif self.target == "s":
                    if engine.thrust_south():
                        ship.msg_contents(thrust_msg)
                    else:
                        notify_failure = True

                elif self.target == "w":
                    if engine.thrust_west():
                        ship.msg_contents(thrust_msg)
                    else:
                        notify_failure = True

                elif self.target == "e":
                    if engine.thrust_east():
                        ship.msg_contents(thrust_msg)
                    else:
                        notify_failure = True

                elif self.target == "reset":
                    if engine.thrust_reset():
                        ship.msg_contents("|GAll thrust reset.")
                    else:
                        notify_failure = True

                elif self.target == "emergency_stop":
                    if engine.emergency_stop():
                        ship.msg_contents("|rAll thrust and forces reset.")
                    else:
                        notify_failure = True

                if notify_failure:
                    ship.msg_contents("Engine was not able to comply.")

class CmdCoreReload(Command):
    """
    Resets your core's processor, clearing and reloading all programs and then starting the simulation again.

    Usage:
       core reload 

    """

    key = "core reload"
    aliases = []
    locks = "cmd:false()"
    help_category = "aiCores and HardcodePrograms"

    def func(self):
        caller = self.caller
        caller.reload()
        caller.msg("Core reloaded.")
                
class CmdCoreLoadProgram(Command):
    """
    Load a program into your aiCore, by it's key.
    This will place the program into the inventory of the aiCore and will take up one of its slots.
    You can get it back by unloading it.

    Usage:
       core load program_key 
    """

    key = "core load"
    aliases = []
    locks = "cmd:false()"
    help_category = "aiCores and HardcodePrograms"

    def func(self):
        caller = self.caller
        try:
            program = caller.search(self.args)
        except:
            pass

        if not program:
            return

        if program:
            if caller.load_program(self.args):
                caller.msg(f"Program ready to |grun.")
            else:
                caller.msg(f"|rFailed to load the program.")

class CmdCoreUnloadProgram(Command):
    """
    Unload a program from your Core, by it's key. This will free up a slot.

    Usage:
       core unload program_key 
    """

    key = "core unload"
    aliases = []
    locks = "cmd:false()"
    help_category = "aiCores and HardcodePrograms"

    def func(self):
        caller = self.caller
        try:
            program = caller.search(self.args)
        except: 
            pass

        if not program:
            caller.msg(f"Cannot find program: {self.args}")

        if program:
            if caller.unload_program(self.args):
                caller.msg(f"A slot has been freed in the core.")
            else:
                caller.msg(f"Core failed to unload the program.")

class CmdCoreRunProgram(Command):
    """
    Run a program that has been loaded into your aiCore, by it's key.
    This will cause your program to be added to the simulation loop.

    Usage:
       core run program_key 
    """

    key = "core run"
    aliases = []
    locks = "cmd:false()"
    help_category = "aiCores and HardcodePrograms"

    def func(self):
        caller = self.caller

        try:
            program = caller.search(self.args)
        except: 
            pass

        if not program:
            caller.msg(f"Cannot find program: {self.args}")

        if program:
            if caller.run_program(self.args):
                caller.msg(f"The core is now running: {self.args}.")
            else:
                caller.msg(f"Core failed to run the program. Is it loaded?")

class CmdCoreKillProgram(Command):
    """
    Kill a program that is running on your aiCore, by it's key.
    This will remove that program from your simulation loop.

    Usage:
       core kill program_key 
    """

    key = "core kill"
    aliases = []
    locks = "cmd:false()"
    help_category = "aiCores and HardcodePrograms"

    def func(self):
        caller = self.caller

        try:
            program = caller.search(self.args)
        except: 
            pass

        if not program:
            caller.msg(f"Cannot find program: {self.args}")

        if program:
            if caller.kill_program(self.args):
                caller.msg(f"The core killed: {self.args}.")
            else:
                caller.msg(f"Core failed to kill the program. Is it running?")

class CmdCoreShowLoadedPrograms(Command):
    """
    Show the loaded programs.

    Usage:
       core ls 
    """

    key = "core ls"
    aliases = []
    locks = "cmd:false()"
    help_category = "aiCores and HardcodePrograms"

    def func(self):
        caller = self.caller

        caller.msg("List of HardcodePrograms:")
        caller.msg(", ".join(program for program in caller.loaded_programs))

class CmdCoreShowRunningPrograms(Command):
    """
    Show the loaded programs.

    Usage:
       core ps 
    """

    key = "core ps"
    aliases = []
    locks = "cmd:false()"
    help_category = "aiCores and HardcodePrograms"

    def func(self):
        caller = self.caller

        caller.msg("Running Programs:")
        caller.msg(", ".join(program for program in caller.running_programs))

class CmdCoreToggleNoisy(Command):
    """
    Have the core report every simulation loops' output.

    Usage:
       core noisy 
    """

    key = "core noisy"
    aliases = []
    locks = "cmd:false()"
    help_category = "aiCores and HardcodePrograms"

    def func(self):
        caller = self.caller
        caller.noisy = not caller.noisy


class CmdCoreShowDataStream(Command):
    """
    View a snapshot of the sensor data being fed to your program.
    These are the facts that allow you to make decisions within your program.

    Usage:
       core datastream 
    """

    key = "core datastream"
    aliases = []
    locks = "cmd:false()"
    help_category = "aiCores and HardcodePrograms"

    def func(self):
        caller = self.caller
        caller.msg("|yDatastream of Connected Sensors:")
        caller.msg(f"|b{caller.view_data_stream()}")

class CmdCoreShowLogs(Command):
    """
    View a the output from loops of your programs.

    Usage:
       core logs 
    """

    key = "core logs"
    aliases = []
    locks = "cmd:false()"
    help_category = "aiCores and HardcodePrograms"

    def func(self):
        caller = self.caller
        caller.msg("\n".join(caller.logs[-10:]))

class CmdCoreShowLastError(Command):
    """
    View the output of the last error that stopped your core's simulation.

    Usage:
       core error 
    """

    key = "core error"
    aliases = []
    locks = "cmd:false()"
    help_category = "aiCores and HardcodePrograms"

    def func(self):
        caller = self.caller

        caller.msg("|yLast Core Simulation Loop Error Before Termination:") 
        caller.msg(caller.last_error)

class CmdCoreClearError(Command):
    """
    Clear the error state from your core to begin the simulation again.

    Usage:
       core clear error
    """

    key = "core clear error"
    aliases = []
    locks = "cmd:false()"
    help_category = "aiCores and HardcodePrograms"

    def func(self):
        caller = self.caller

        caller.clear_failure()
        caller.last_error = None
        caller.failure = False
        caller.reload()

        caller.msg("Core simulation loop started.")

class CmdCoreShowProgram(Command):
    """
    Show the entire program the core will run in the loop.

    Usage:
       core show program
    """

    key = "core show program"
    aliases = []
    locks = "cmd:false()"
    help_category = "aiCores and HardcodePrograms"

    def func(self):
        caller = self.caller

        caller.msg("|yCore simulation loop:")
        caller.msg(f"|b{caller.program()}")

class CmdCoreLinkTo(Command):
    """
    Link your core to another subsystem. If you provide two arguments, it will link that system to the other system.

    Usage:
        core link SUBSYSTEM [OTHER_SUBSYSTEM]

    Example:
        core link reactor
        core link reactor battery
        core link battery radar
        core link battery engine
    """
    key = "core link"
    aliases = []
    locks = "cmd:false()"
    help_category = "aiCores and HardcodePrograms"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("|rError. |yMust provide at least |gone subsystem |yto link the |bcore|y to, or |gtwo subsystems|n to link together.")

        arg1 = self.args.split(" ")[0]

        arg2 = self.args.split(" ")[-1]

        if arg1 == arg2:
            target = caller.search(arg1)

            if caller.link_to(target):
                caller.msg(f"Core linked to {arg1} successfully.")

        else:
            first_subsystem = caller.search(arg1)
            if not first_subsystem:
                return

            second_subsystem = caller.search(arg2)
            if not second_subsystem:
                return

            if first_subsystem.link_to(second_subsystem):
                caller.msg(f"{arg1} linked to {arg2} successfully")

class CmdProgramEdit(Command):
    """
    Edit a program with an interactive editor. Insert, delete, replace functions.

    Usage:
        program edit NAME
    """
    key = "program edit"
    aliases = []
    locks = "cmd:all()"
    help_category = "aiCores and HardcodePrograms"

    def func(self):
        caller = self.caller
        if self.args != '':
            target = caller.search(self.args)

            if not target:
                target = create.create_object("prolog.hardcodable.HardcodeProgram", key=self.args )
                target.location = caller

            if hasattr(target, "hardcode_content"):
                target.edit_program(caller)
        else:
            caller.msg("You must provide a name of the program to edit.")

class CmdProgramTest(Command):
    """
    Test a program. You must be near a core so that the program can be tested with sensor data.

    Usage:
        program test NAME
    """
    key = "program test"
    aliases = []
    locks = "cmd:all()"
    help_category = "aiCores and HardcodePrograms"

    def func(self):
        caller = self.caller
        target = caller.search(self.args)

        if not target:
            return

        if hasattr(target, "hardcode_content"):
            target.test_program(caller)

class CmdLook(Command):
    key = "look"
    aliases = []
    locks = "cmd:false()"
    help_category = "aiCores and HardcodePrograms"

    def func(self):
        pass

class CoreCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdCoreReload)
        self.add(CmdCoreLoadProgram)
        self.add(CmdCoreUnloadProgram)
        self.add(CmdCoreRunProgram)
        self.add(CmdCoreKillProgram)
        #self.add(CmdCoreEditProgram)
        #self.add(CmdCoreShowSpecs)
        self.add(CmdCoreShowDataStream)
        self.add(CmdCoreShowLogs)
        self.add(CmdCoreShowLastError)
        self.add(CmdCoreClearError)
        self.add(CmdProgramEdit)
        self.add(CmdProgramTest)
        self.add(CmdCoreShowLoadedPrograms)
        self.add(CmdCoreShowRunningPrograms)
        self.add(CmdCoreToggleNoisy)
        self.add(CmdCoreLinkTo)
        self.add(CmdCoreShowProgram)
        self.add(CmdLook)

class RadarCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdRadarPulse)

class EngineCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdEngineThrust)

class VehiclePilotingCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdDisembarkVehicle())
        self.add(CmdPowerOnVehicle())
        self.add(CmdPowerOffVehicle())
        self.add(CmdPilotLaunch())
        self.add(CmdPilotDock())

class VehicleEntryCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdPilotVehicle())

class SpaceRoom(DefaultRoom, Simulatable):
    width = AttributeProperty(default=1000)
    height = AttributeProperty(default=1000)

    def at_server_reload(self):
        print("Simulation needs to cleaup! reload happening!")

        self.to_simulate = {}

        return True

    def at_init(self):
        #print("Simulation initializing! getting contents.")
        for item in self.contents:
            if hasattr(item, "newtonian_data") and hasattr(item, "to_fact"):
                self.track(item)
        return True

    def program(self):
        with open('prolog/moving_bodies_simulation.pl', 'r') as file:
            content = file.read()
        return content

    def update(self, model):
        for fact in model.symbols(shown=True):
            # print(fact)
            # time_body_position(T, B, Px, Py, Vx, Vy)
            # time_body_position(1,14,20,22,0,0)
            time_step, body, px, py, vx, vy = [int(strPart) for strPart in str(fact).replace("time_body_position(", "").replace(")", "").split(",")]

            if body in self.to_simulate:
                entity = self.to_simulate[body]

                fx = entity.newtonian_data["Fx"]
                fy = entity.newtonian_data["Fy"]
                entity.newtonian_data["x"] = px
                entity.newtonian_data["y"] = py
                entity.newtonian_data["Vx"] = vx
                entity.newtonian_data["Vy"] = vy

                if vx > 0 or vx < 0 or vy > 0 or vy < 0:
                    entity.newtonian_data["wasMoving"] = True
                    if hasattr(entity, "aiCore"):
                        entity.aiCore.update_status()
                else:
                    if entity.newtonian_data["wasMoving"] == True:
                        entity.newtonian_data["wasMoving"] = False
                        entity.msg_contents(f"You have come to rest. \n|rPos: {px},{py} |bVelocity: {vx},{vy} |gForce: {fx}, {fy}|n")


    def at_object_leave(self, moved_obj, target_location, move_type="move", **kwargs):
        try:
            if hasattr(moved_obj, "newtonian_data") and hasattr(moved_obj, "to_fact"):
                self.ignore(moved_obj)
        except Exception as e:
            print(e)
        finally:
            return True

    def at_pre_object_receive(self, arriving_object, source_location, **kwargs):
        try:
            if hasattr(arriving_object, "newtonian_data") and hasattr(arriving_object, "to_fact"):
                self.track(arriving_object)
        except Exception as e:
            print(e)
        finally:
            return True

    def item_nearby(self, item, x, y):
        return item.newtonian_data["x"] <= x + 10 and item.newtonian_data["x"] >= x - 10 and item.newtonian_data["y"] <= y + 10 and item.newtonian_data["y"] >= y - 10

    def get_contents_at_position(self, x, y):
        items = []
        for item in self.contents:
            if item.newtonian_data["x"] == x and item.newtonian_data["y"] == y:
                items.append(item)

        return items

    def get_contents_near_position(self, x, y):
        nearby = []
        for item in self.contents:
            if self.item_nearby(item, x, y):
                nearby.append(item)

        return nearby

    def symbol_for_obj(self, obj):
        pass

    def objects_here(self, x, y, nearby):
        objects = []
        for item in nearby:
            if item.newtonian_data["x"] == x and item.newtonian_data["y"] == y:
                objects.append(item)

        return objects


    def render_row(self, row_y, origin_x, nearby):
        output = f"{row_y:+05} | "
        empty_space = ". "

        for i in range(origin_x - 10,origin_x + 10 + 1):
            objects_at_location = self.objects_here(i, row_y, nearby)
            if len(objects_at_location) > 0:
                output += "@ "
            else:
                output += empty_space

        return output

    def render_map(self, caller=None):
        if caller == None:
            return None

        origin_x = caller.location.newtonian_data["x"]
        origin_y = caller.location.newtonian_data["y"]

        # get contents
        nearby = self.get_contents_near_position(origin_x, origin_y)

        rows = []

        rows.append("")
        for i in range(origin_y - 10, origin_y + 10 + 1):
            rows.append(self.render_row(i, origin_x, nearby))

        rows.append("      -------------------------------------------")
        rows.append(f"                     x:{origin_x:+05}")
        rows.append("")

        rows.reverse()
        return "\n".join(rows)

class SpaceRoomDock(Object):
    exit_room = AttributeProperty(default=None)
    pass
