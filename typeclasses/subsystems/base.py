from evennia import Command, CmdSet, CmdSet, AttributeProperty
from evennia import TICKER_HANDLER as tickerhandler

from ..objects import Object

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
        self.location.update_prompt(self.location.pilot)

        if self.provides_cmdset_named != None:
            self.location.pilot.cmdset.add(self.provides_cmdset_named)

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

    def emergency_stop(self):
        self.location.msg_contents("You feel your guts slam around as the emergency stop is performed, alarm sirens blaring.")
        self.location.at_power_off()

        self.location.newtonian_data["Fx"] = 0
        self.location.newtonian_data["Fy"] = 0
        self.location.newtonian_data["Vx"] = 0
        self.location.newtonian_data["Vy"] = 0


class DefaultCore(Subsystem):
    energyConsumedPerTickPerLevel = AttributeProperty(default=0)
    name = "Stock AI Core"
    HUDname = "core"

class DefaultReactor(Subsystem):
    energyProvidedPerTick = AttributeProperty(default=10)
    energyTransferredPerTick = AttributeProperty(default=10)
    energyConsumedPerTickPerLevel = AttributeProperty(default=0)
    fuelConsumedPerTickPerLevel = AttributeProperty(default=1)
    storedFuel = AttributeProperty(default=30)
    energyCapacity = AttributeProperty(default=10)
    HUDname = "reactor"
    name = "Stock Reactor"

class DefaultBattery(Subsystem):
    name = "Stock Battery"
    HUDname = "battery"
    energyCapacity = AttributeProperty(default=30)
    energyConsumedPerTickPerLevel = AttributeProperty(default=0)
    energyTransferredPerTick = AttributeProperty(default=5)

class DefaultRadar(Subsystem):
    energyCapacity = AttributeProperty(default=10)
    energyConsumedPerTickPerLevel = AttributeProperty(default=1)
    name = "Stock Radar"
    HUDname = "radar"
    provides_cmdset_named = "typeclasses.objects.RadarCmdSet"

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
