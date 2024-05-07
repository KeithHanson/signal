from evennia import Command, CmdSet, CmdSet, AttributeProperty
from evennia import TICKER_HANDLER as tickerhandler

from ..characters import Character

from ..objects import Object

from prolog.hardcodable import Hardcodable

from textwrap import dedent

class Subsystem(Object):
    name = AttributeProperty(default="Subsystem Name")

    HUDname = AttributeProperty(default="subname")

    fuelCapacity = AttributeProperty(default=0)
    storedFuel = AttributeProperty(default=0)

    fuelConsumedPerTickPerLevel = AttributeProperty(default=0)

    assignedEnergyLevel = AttributeProperty(default=0) # 0-5

    energyConsumedPerTickPerLevel = AttributeProperty(default=10)

    energyProvidedPerTick = AttributeProperty(default=0)

    energyTransferredPerTick = AttributeProperty(default=0)

    linkedSubsystems = AttributeProperty(default=[])

    # Represents basic capacitor storage within the subsystem's circuitry
    energyCapacity = AttributeProperty(default=10)

    storedEnergy = AttributeProperty(default=0)

    powered = AttributeProperty(default=False)

    provides_cmdset_named = None

    def at_object_creation(self):
        pass

    def get_prompt_text(self):
        sub_powered_color = "|g" if self.powered else "|r"
        stored_fuel_str = "(F" + str(self.storedFuel) + ")" if self.storedFuel > 0 else ""
        stored_energy_str = "(E" + str(self.storedEnergy) + ")"
        return sub_powered_color + self.HUDname + ":" + str(self.assignedEnergyLevel) + stored_fuel_str + stored_energy_str

    def link_to(self, receiver):
        if self.linkedSubsystems == None:
            self.linkedSubsystems = []

        self.db.linkedSubsystems.append(receiver)
        self.save()
        return True

    def unlink(self, receiver):
        if self.linkedSubsystems == None:
            self.linkedSubsystems = []

        if receiver in self.db.linkedSubsystems:
            self.db.linkedSubsystems.remove(receiver)

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
        fuel_draw = self.fuelConsumedPerTickPerLevel * self.assignedEnergyLevel

        if self.storedFuel >= fuel_draw:
            self.storedFuel = self.storedFuel - fuel_draw
            
            amount_to_store = self.energyProvidedPerTick if self.energyProvidedPerTick < self.energyCapacity - self.storedEnergy else self.energyCapacity - self.storedEnergy

            self.storedEnergy = self.storedEnergy + amount_to_store
        else:
            self.at_power_off()
            
            self.location.msg_contents(f"{self.name} falters and powers off as it runs out of fuel.")
            pass

    def transfer_energy(self, receiver):
        if self.powered:
            amount_to_transfer = self.energyTransferredPerTick if self.energyTransferredPerTick < receiver.energyCapacity - receiver.storedEnergy else receiver.energyCapacity - receiver.storedEnergy
            if amount_to_transfer > self.storedEnergy:
                amount_to_transfer = self.storedEnergy

            self.storedEnergy = self.storedEnergy - amount_to_transfer 

            receiver.storedEnergy = receiver.storedEnergy + amount_to_transfer

        else:
            pass

    def consume_energy(self):
        if self.powered:
            power_draw = self.energyConsumedPerTickPerLevel * self.assignedEnergyLevel

            if self.storedEnergy >= power_draw:
                self.storedEnergy = self.storedEnergy - power_draw
                self.at_consume_energy()
            else:
                if power_draw > 0:
                    self.location.msg_contents(f"{self.name} falters as it cannot draw enough power. Stored Energy: {self.storedEnergy} Power Draw: {power_draw}")
                    self.at_power_off()

    # Override in each type of module to do the things.
    def at_consume_energy(self):
        pass

    def at_power_on(self):
        tickerhandler.add(1, self.at_tick)
        self.powered = True
        self.assignedEnergyLevel = 1
        #self.location.update_prompt(self.location.pilot)

        if self.provides_cmdset_named != None:
            self.cmdset.add(self.provides_cmdset_named)

        if isinstance(self, Hardcodable): 
            for item in self.location.contents:
                if hasattr(item, "to_fact"):
                    self.add_sensor(item)

    def at_power_off(self):
        try:
            tickerhandler.remove(1, self.at_tick)

            if self.provides_cmdset_named != None:
                self.location.pilot.cmdset.delete(self.provides_cmdset_named)
        except Exception as e:
            pass

        self.powered = False
        self.assignedEnergyLevel = 0
        self.storedEnergy = 0
        self.location.update_prompt(self.location.pilot)

class DefaultEngine(Subsystem):
    energyCapacity = AttributeProperty(default=10)
    energyConsumedPerTickPerLevel = AttributeProperty(default=1)
    thrustOutputPerLevel = AttributeProperty(default=1)
    provides_cmdset_named = "typeclasses.objects.EngineCmdSet"
    name = "Stock Engine"
    HUDname = "engine"

    def to_fact(self):
        return dedent(f"""
        % Engine Facts
        % engine(HUDname, thrustOutputPerLevel, energyConsumedPerTickPerLevel, energyCapacity, storedEnergy).
        engine({self.HUDname}, {self.thrustOutputPerLevel}, {self.energyConsumedPerTickPerLevel}, {self.energyCapacity}, {self.storedEnergy}).
        """)

    def thrust_north(self):
        desired_thrust_level = self.location.newtonian_data["Fy"] + 1
        current_max_thrust_level = self.thrustOutputPerLevel * self.assignedEnergyLevel
        if  desired_thrust_level <= current_max_thrust_level:
            self.location.newtonian_data["Fy"] += 1
            return True
        else: 
            return False

    def thrust_south(self):
        desired_thrust_level = self.location.newtonian_data["Fy"] - 1

        current_max_thrust_level = self.thrustOutputPerLevel * self.assignedEnergyLevel

        if  abs(desired_thrust_level) <= current_max_thrust_level:
            self.location.newtonian_data["Fy"] -= 1
            return True
        else: 
            return False

    def thrust_west(self):
        desired_thrust_level = self.location.newtonian_data["Fx"] - 1

        current_max_thrust_level = self.thrustOutputPerLevel * self.assignedEnergyLevel

        if  abs(desired_thrust_level) <= current_max_thrust_level:
            self.location.newtonian_data["Fx"] -= 1
            return True
        else: 
            return False

    def thrust_east(self):
        desired_thrust_level = self.location.newtonian_data["Fx"] + 1
        current_max_thrust_level = self.thrustOutputPerLevel * self.assignedEnergyLevel
        if  desired_thrust_level <= current_max_thrust_level:
            self.location.newtonian_data["Fx"] += 1
            return True
        else: 
            return False

    def thrust_reset(self):
        self.location.newtonian_data["Fx"] = 0
        self.location.newtonian_data["Fy"] = 0
        return True

    def emergency_stop(self):
        self.location.msg_contents("You feel your guts slam around as the emergency stop is performed, alarm sirens blaring.")
        self.location.at_power_off()

        self.location.newtonian_data["Fx"] = 0
        self.location.newtonian_data["Fy"] = 0
        self.location.newtonian_data["Vx"] = 0
        self.location.newtonian_data["Vy"] = 0

        return True


class DefaultCore(Subsystem, Hardcodable, Character):
    energyConsumedPerTickPerLevel = AttributeProperty(default=0)
    name = "Stock AI Core"
    HUDname = "core"
    provides_cmdset_named = "typeclasses.objects.CoreCmdSet"

    def at_post_puppet(self, **kwargs):
        """
        Called just after puppeting has been completed and all
        Account<->Object links have been established.

        Args:
            **kwargs: Arbitrary, optional arguments for users
                overriding the call (unused by default).
        Notes:
            You can use `self.account` and `self.sessions.get()` to get account and sessions at this
            point; the last entry in the list from `self.sessions.get()` is the latest Session
            puppeting this Object.

        """
        self.account.db._last_puppet = self
        self.msg("|gSignal|yOS |bInitializing... |g[OK]")
        self.msg("|yTesting basic sentience interface... |g[OK]")
        self.msg("|yBootstrapping quantum entanglement... |g[OK]")
        self.msg("|yConnecting to available sensors... |g[OK]")
        self.msg("|yFinal diagnostic tests... |g[OK]")
        self.msg("|rCore |gReady for Sentience.")

    def at_init(self):
        self.at_power_on()

    def execute_command(self, command):
        if self.location.pilot:
            self.location.pilot.execute_cmd(command)

    def to_fact(self):
        if hasattr(self.location, "to_fact"):
            return self.location.to_fact()
        else:
            self.msg("|yYou have not been installed into a location with sensors. |nYou should |rpanic.")

class DefaultReactor(Subsystem):
    energyProvidedPerTick = AttributeProperty(default=10)
    energyTransferredPerTick = AttributeProperty(default=10)
    energyConsumedPerTickPerLevel = AttributeProperty(default=0)
    fuelConsumedPerTickPerLevel = AttributeProperty(default=1)
    storedFuel = AttributeProperty(default=30)
    energyCapacity = AttributeProperty(default=10)
    HUDname = "reactor"
    name = "Stock Reactor"

    def to_fact(self):
        return dedent(f"""
        % Reactor Facts
        % reactor(HUDname, energyProvidedPerTick, energyTransferredPerTick, EnergyConsumedPerTickPerLevel, fuelConsumedPerTickPerLevel, storedFuel, energyCapacity, storedEnergy).
        reactor({self.HUDname}, {self.energyProvidedPerTick}, {self.energyTransferredPerTick}, {self.energyConsumedPerTickPerLevel}, {self.fuelConsumedPerTickPerLevel}, {self.storedFuel}, {self.energyCapacity}, {self.storedEnergy}).
        """)

class DefaultBattery(Subsystem):
    name = "Stock Battery"
    HUDname = "battery"
    energyCapacity = AttributeProperty(default=30)
    energyConsumedPerTickPerLevel = AttributeProperty(default=0)
    energyTransferredPerTick = AttributeProperty(default=5)

    def to_fact(self):
        return dedent(f"""
        %Battery Facts
        %battery(HUDname, energyTransferredPerTick, energyCapacity, storedEnergy).
        battery({self.HUDname}, {self.energyTransferredPerTick}, {self.energyCapacity}, {self.storedEnergy}).
        """)

class DefaultRadar(Subsystem):
    energyCapacity = AttributeProperty(default=10)
    energyConsumedPerTickPerLevel = AttributeProperty(default=1)
    name = "Stock Radar"
    HUDname = "radar"
    provides_cmdset_named = "typeclasses.objects.RadarCmdSet"

    def to_fact(self):
        return dedent(f"""
        %Radar Facts

        %radar(HUDname, energyConsumedPerTickPerLevel, energyCapacity, storedEnergy).
        radar({self.HUDname}, {self.energyConsumedPerTickPerLevel}, {self.energyCapacity}, {self.storedEnergy}).

        %Radar Last Pulse Location, -1,-1 if never pulsed.
        %lastPulseLocation(X, Y)
        %lastPulseLocation(-1,-1).

        %Radar Last Pulse Targets
        %pulseResult(#ID, X, Y).
        """)

    def pulse(self, caller, space_room):
        power_draw = self.energyConsumedPerTickPerLevel * self.assignedEnergyLevel

        if self.storedEnergy >= power_draw:
            self.storedEnergy -= power_draw
            # Basic implementation, render the map perfectly from the space_room
            caller.msg("")
            caller.msg(space_room.render_map(caller))
            caller.msg("You feel a brief burst of electrical energy as your radar pulses and its capacitors drain.")

        else:
            caller.msg("Your radar doesn't have enough energy to pulse yet.")
