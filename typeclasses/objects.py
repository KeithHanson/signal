"""
Object

The Object is the "naked" base class for things in the game world.

Note that the default Character, Room and Exit does not inherit from
this Object, but from their respective default implementations in the
evennia library. If you want to use this class as a parent to change
the other types, you can do so by adding this as a multiple
inheritance.

"""

from evennia.objects.objects import DefaultObject
from evennia import Command, CmdSet, CmdSet, AttributeProperty
from evennia import TICKER_HANDLER as tickerhandler
import evennia



class ObjectParent:
    """
    This is a mixin that can be used to override *all* entities inheriting at
    some distance from DefaultObject (Objects, Exits, Characters and Rooms).

    Just add any method that exists on `DefaultObject` to this class. If one
    of the derived classes has itself defined that same hook already, that will
    take precedence.

    """


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


# TODO: Provide new commands at power on and remove them at power off
class Subsystem(Object):
    name = AttributeProperty(default="Subsystem Name")

    HUDname = AttributeProperty(default="subname")

    fuelCapacity = AttributeProperty(default=100)
    storedFuel = AttributeProperty(default=100)

    fuelConsumedPerTickPerLevel = AttributeProperty(default=1)

    assignedEnergyLevel = AttributeProperty(default=0) # 0-5

    energyConsumedPerTickPerLevel = AttributeProperty(default=10)

    energyProvidedPerTick = AttributeProperty(default=0)

    energyTransferredPerTick = AttributeProperty(default=0)

    linkedSubsystems = AttributeProperty(default=[])

    # Represents basic capacitor storage within the subsystem's circuitry
    energyCapacity = AttributeProperty(default=10)

    storedEnergy = AttributeProperty(default=0)

    powered = AttributeProperty(default=False)

    def link_to(self, receiver):
        if self.db.linkedSubsystems == None:
            self.db.linkedSubsystems = []
            self.db.linkedSubsystems.append(receiver)
            self.save()

    # TODO: Handle damaging power levels
    def at_tick(self):
        # Generate Energy
        if self.energyProvidedPerTick > 0:
            self.generate_energy()

        # loop over each connected subsystem
        # TODO: Priority order
        for subsystem in self.linkedSubsystems:
            # Transfer energy
            if self.energyTransferredPerTick > 0:
                self.transfer_energy(subsystem)

            # Consume energy (do the work) - fires at_consume_energy
            if self.energyConsumedPerTickPerLevel > 0:
                self.consume_energy()
        pass

    def generate_energy(self):
        fuel_draw = self.fuelConsumedPerTickPerLevel * assignedEnergyLevel

        if self.storedFuel > fuel_draw:
            self.storedFuel = self.storedFuel - fuel_draw

            self.storedEnergy = self.storedEnergy + self.energyProvidedPerTick * assignedEnergyLevel
        else:
            self.at_power_off()
            
            self.location.msg_content(f"{self.name} falters and powers off as it runs out of fuel.")

            pass

    def transfer_energy(self, receiver):
        receiver_power_draw = receiver.energyConsumedPerTickPerLevel * receiver.assignedEnergyLevel

        if self.storedEnergy > self.energyTransferredPerTick:
            amount_to_transfer = self.energyTransferredPerTick

            if receiver_power_draw < amount_to_transfer:
                amount_to_transfer = receiver_power_draw

            self.storedEnergy = self.storedEnergy - amount_to_transfer 

            receiver.storedEnergy = receiver.storedEnergy + amount_to_transfer


    def consume_energy(self):
        if self.powered:
            power_draw = self.energyConsumedPerTickPerLevel * self.assignedEnergyLevel

            if self.storedEnergy > power_draw:
                self.storedEnergy = self.storedEnergy - power_draw
                self.at_consume_energy()
            else:
                self.location.msg_content(f"{self.name} falters as it cannot draw enough power")
                self.at_power_off()

    # Override in each type of module to do the things.
    def at_consume_energy(self):
        pass

    def at_power_on(self):
        tickerhandler.add(1, self.at_tick)
        self.powered = True
        self.msg_content(f"{self} Powered on.")

    def at_power_off(self):
        tickerhandler.remove(1, self.at_tick)
        self.powered = False
        self.msg_content(f"{self} Powered off.")

class DefaultReactor(Subsystem):
    energyProvidedPerTick = AttributeProperty(1)

    def at_object_creation(self):
        self.name = "Stock Reactor"


class DefaultEngine(Subsystem):
    energyConsumedPerTickPerLevel = AttributeProperty(1)
    thrustOutputPerLevel = AttributeProperty(1)

    name = "Stock Engine"

class DefaultCore(Subsystem):
    energyConsumedPerTickPerLevel = AttributeProperty(0)
    name = "Stock AI Core"

class DefaultRadar(Subsystem):
    energyConsumedPerTickPerLevel = AttributeProperty(1)
    name = "Stock Radar"

class DefaultBattery(Subsystem):
    name = "Stock Battery"
    energyCapacity = AttributeProperty(1000)
    energyConsumedPerTickPerLevel = AttributeProperty(1)


class Vehicle(Object):
    armor = AttributeProperty(default=0)
    pilot = AttributeProperty(None)

    powered = AttributeProperty(False)
    
    aiCore = AttributeProperty(None)

    def get_display_desc(self, looker, **kwargs):
        if self.powered:
            return self.db.desc + " The vehicle hums quietly, powered and ready for flight. " + "Subsystems: " + str(len(self.aiCore.linkedSubsystems))
        else:
            return self.db.desc + " The vehicle sits silently, powered off, awaiting it's pilot. " + "Subsystems: " + str(len(self.aiCore.linkedSubsystems))

    def at_object_creation(self):
        self.cmdset.add_default('typeclasses.objects.VehicleEntryCmdSet')

        core = evennia.create_object('typeclasses.objects.DefaultCore', key="stock_core", location=self)

        reactor = evennia.create_object('typeclasses.objects.DefaultReactor', key="stock_reactor", location=self)
        core.link_to(reactor)

        battery = evennia.create_object('typeclasses.objects.DefaultBattery', key="stock_battery", location=self)
        reactor.link_to(battery)

        engine = evennia.create_object('typeclasses.objects.DefaultEngine', key="stock_engine", location=self)
        battery.link_to(engine)

        radar = evennia.create_object('typeclasses.objects.DefaultRadar', key="stock_radar", location=self)
        battery.link_to(radar)

        self.aiCore = core
        self.save()

    def at_pilot_enter(self, pilot):
        self.location.msg_contents("$You() $conj(open) the hatch and $conj(enter) the vehicle, the seal closing with a hiss.", from_obj=pilot)

        self.pilot = pilot
        pilot.location = self

        self.pilot.cmdset.add("typeclasses.objects.VehiclePilotingCmdSet")


    def at_pilot_exit(self, pilot):

        self.pilot = None

        self.msg_contents("The vehicle door opens with a hiss as the airlock unseals, and $You() $conj(exit) the vehicle.", from_obj=pilot)
        self.location.msg_contents("The vehicle door opens with a hiss as the airlock unseals, and $You() $conj(exit) the vehicle.", from_obj=pilot)

        pilot.move_to(self.location)

        pilot.cmdset.delete("typeclasses.objects.VehiclePilotingCmdSet")

    def at_power_on(self):
        self.powered = True
        self.pilot.msg("You feel the engines rumble to life. Your HUD begins to boot, and blinking lights spring to life.")

        self.location.msg("You feel a rumble in your chest as {key} powers up and begins levitating.")

        self.core.at_power_on()

    def at_power_off(self):
        self.powered = False
        self.location.msg("As the vehicle powers off, it lands softly on the ground.")
        self.pilot.msg("You feel the vehicle land softly and watch as your subsystems power off.")
        self.core.at_power_off()

    def at_object_delete(self):
        for cur_system in self.contents:
            if cur_system:
                cur_system.location = evennia.settings.DEFAULT_HOME
                cur_system.delete()

        return True

class DefaultSpaceShip(Vehicle):
    def at_object_creation(self):
        super().at_object_creation()
        pass

class CmdPilotVehicle(Command):
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

    def parse(self):
        self.target = self.caller.search(self.args.strip())

    def func(self):
        caller = self.caller

        if not self.target or self.target == "here":
            caller.msg("Pilot what?")
        else:
            target = caller.search(self.target)
            if not target:
                caller.msg("Couldn't find that to pilot.")

            target.at_pilot_enter(caller)

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


class VehiclePilotingCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdDisembarkVehicle())
        self.add(CmdPowerOnVehicle())
        self.add(CmdPowerOffVehicle())

class VehicleEntryCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdPilotVehicle())
