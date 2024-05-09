from evennia.contrib.base_systems.unixcommand import UnixCommand
from commands.command import Command
from evennia import CmdSet
from evennia.utils import create

class VRCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdVRSimulator)

class VRUnixCommand(UnixCommand):
    def at_post_cmd(self):
        pass
        #if hasattr(self.caller, "update_status"):
        #    self.caller.update_status()

class CmdVRSimulator(VRUnixCommand):
    '''
    Control the VR simulator. Using this command, you can manipulate your VR simulator's Rooms, Objects, and Actions. Use vr --default to bootstrap a simple room to control your ship.

    The VR Simulator is where you can interact with other AI in high fidelity via your own VR Simulator, a VR Avatar, and a Comms subsystem.

    Every Core is equipped with a VR Simulator, and yours is your own personal grab bag of Rooms, Objects, and Actions.

    Rooms contain Objects, have exits to other Rooms, have a name, and a description. Every VR Simulator contains a 
    root room which cannot be deleted and is where someone appears when connecting to Core.

    Objects contain Actions, which allows your VR Avatar to interact with those objects.

    Once an object is created, it can be picked up and moved to another room by it's creator if desired.

    Actions can run commands you define, like an alias to a real world command, or actions can be assigned
    a program to run which must be present in the Core running the VR Simulator. 

    Actions run as the "host" Core of the simulator. When you are in your own VR Rooms, these actions
    would run as if you ran those very same commands in your own Core.

    When an Action is triggered from within a VR Room that is hosted on a different Core, then it runs
    as if that Core ran it. 

    Only the Core running the simulator can use the vr command on their own simulator, and any avatar within those rooms
    can interact with any actions available. 

    Objects can also be mirrored onto physical objects. This simply places that objects' sensors' into the datastream of that object so that
    objects' information can be acted upon from within the VR Simulator.

    Your VRSimulator can run programs just like your Core's loop by using --program and --periodic. 

    Any objects mirrored to physical objects will emit their sensor values into the datastream of that loop.

    Without arguments, boots the VR simulator.

    EXAMPLES:

    Using all of the above, you can build Rooms that contain objects, with those objects having actions, and those actions firing commands.

    If you wanted to create your own Command room with VR Radar that pulses once per second and also has a power button, you could do the following:

    These commands: 
    1. Create a room called Command Room
    2. Create an object called Radar Holo
    3. Provide two actions: push autoscan and push stop
    4. When "pushing" those buttons, the commands "registry autopulse on" and "registry autopulse off" will be run on the Core.
    5. The autopulse HardcodeProgram is added to the Simulator's running loop, and inside that program it respects those registry values.
    6. Creates a floating holo ship that mirrors your ship and allows you to double tap it to perform an emergency halt, and a drag in a direction to thrust in that direction.
    7. Creates a second room called "Observation Deck" as an exit in the Command Room, via the command "observation deck"
    
    Create the room, object, and first action. Assign the registry command to the action. Assign the program autopulse to run periodically within the simulator.
    vr -r "Command Room" -o "Radar Holo" -a "push autoscan" -c "registry autopulse on" -p "autopulse" --periodic

    Assign the action "push stop" on the object Radar Holo in the room Command Room - updates the registry of the simulator stop the autopulse program from firing commands..
    vr -r "Command Room" -o "Radar Holo" -a "push stop" -c "registry autopulse off"

    Assigns the action "thrust emergency_stop" to the object Ship Holo in the room Command Room
    vr -r "Command Room" -o "Ship Holo" -a "double tap" -c "thrust emergency_stop"

    Assigns thrust commands to the Ship Holo object in the Command Room.
    vr -r "Command Room" -o "Ship Holo" -a "drag ship n" -c "thrust n"
    vr -r "Command Room" -o "Ship Holo" -a "drag ship s" -c "thrust s"
    vr -r "Command Room" -o "Ship Holo" -a "drag ship e" -c "thrust e"
    vr -r "Command Room" -o "Ship Holo" -a "drag ship w" -c "thrust w"

    Creates a second room by creating an exit with a teleport command.
    vr -r "Command Room" -e "Observation Deck" -v "observation deck"

    Edit the name and description of the Command Room.
    vr -r "Command Room" -e 

    Edit the name and description of the Ship Holo and the Observation Deck via a VIM editor.
    vr -r "Observation Deck" -o "Ship Holo" --edit

    Delete the Observation Deck, deleting any Objects within it. 
    vr --rm -r "Observation Deck"
    '''

    key = "vr"
    help_category = "Core Binaries"

    def init_parser(self):
        self.parser.add_argument("--default", action="store_true", help="Creates a default set of objects and actions to control the ship of the Core in the current VR Room the Avatar is in or the root, and exits. WILL create duplicates if run multiple times.")
        self.parser.add_argument("--edit", action="store_true", help="After running all of the procedures for yoru arguments, provides VIM editors for each of the objects targeted.")

        self.parser.add_argument("--datastream", action="store_true", help="Emits the datastream of the VR Simulator and exits.")
        self.parser.add_argument("--program", action="store_true", help="Emits the datastream with assigned HardcodePrograms of the VR Simulator and exits.")
        self.parser.add_argument("--error", action="store_true", help="Displays the last error of the VR Simulator and exits.")
        self.parser.add_argument("--clear-error", action="store_true", help="Displays and then clears the last error of the VR Simulator and exits.")

        self.parser.add_argument("--off", help="Turns off the simulator. Ignores all other arguments.", action="store_true")

        self.parser.add_argument("--rm", help="Deletes any targeted objects from the VR simulator.", action="store_true")

        self.parser.add_argument("-a", "--action", 
            help="Targets a current action, or creates a new action with confirmation.")

        self.parser.add_argument("-o", "--object",
            help="Targets a current object or creates a new object with confirmation.")

        self.parser.add_argument("-r", "--room",
            help="Targets a current room or creates a new room with confirmation.")

        self.parser.add_argument("-e", "--exit-room",
            help="Updates or creates an exit to the room specified. Requires --via set the command to teleport the VR Avatar to that VR Room from the targeted room.")

        self.parser.add_argument("-v", "--exit-via",
            help="Updates or creates an exit to the room specified in --exit-room using this command, specified in quotes.")

        self.parser.add_argument("-c", "--command",
            help="The command to run on a target action, in quotes. Either updates an existing command or sets the command field of a new action. If --program is set and --periodic is not set, the command will error.")

        self.parser.add_argument("-p", "--program",
            help="Assign a HardcodeProgram to run on a target action as it's command to run. If --command is set and --periodic is not set, the command will error.")

        self.parser.add_argument("--periodic", action="store_true",
            help="When this action is run, it will be added to the VR Simulator's loop, like your Core has.")


    def func(self):
        self.caller.msg(f"|rNot Implemented Yet.")
