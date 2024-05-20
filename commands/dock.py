from evennia.contrib.base_systems.unixcommand import UnixCommand
from commands.command import Command
from evennia import CmdSet
#from evennia.utils import create

class DockCmdSet(CmdSet):
    def at_cmdset_creation(self):
        pass

class CmdDockListShips(UnixCommand):
   '''
   List the ships currently in the dock with you.
   '''

   key = "dls"
   help_category = "Docked Commands"

   def init_parser(self):
       pass

   def func(self):
       caller = self.caller
       dock = self.obj

       # Search for all ship objects in the same location 

class CmdDockInstall(UnixCommand):
   '''
   Install a Core in your cargo hold into a ship with an empty aiCore.
   '''

   key = "install"
   help_category = "Docked Commands"

   def init_parser(self):
       self.parser.add_argument("core", help="The core you wish to install somewhere.")
       self.parser.add_argument("ship", help="The ship you would like to install a core into.")

   def func(self):
       caller = self.caller
       dock = self.obj

       core_to_install = caller.search(self.opts.core)
       ship_to_receive = caller.location.location.search(self.opts.ship)

       if ship_to_receive.aiCore not None:
           caller.msg("Unable to install core. Ship already has a core.")

        core_to_install.location = ship_to_receive
        ship_to_receive.aiCore = core_to_install

        caller.msg("A video feed pops into you consciousness as the dock reaches an autonomous arm carefully into your hold, moves along its tracks to the ship you designated, and gently slots the core into the ship.")
        caller.msg("Installation complete.")
