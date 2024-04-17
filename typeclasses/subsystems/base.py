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

    def link_to(self, receiver):
        if self.linkedSubsystems == None:
            self.linkedSubsystems = []

        self.db.linkedSubsystems.append(receiver)
        self.save()

    # TODO: Handle damaging power levels
    def at_tick(self):
        print(f"{self} TICKING")
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
        print(f"{self} generating energy. Fuel Draw: {fuel_draw}.")

        if self.storedFuel > fuel_draw:
            print(f"{self} energy per tick: {self.energyProvidedPerTick}")
            self.storedFuel = self.storedFuel - fuel_draw

            self.storedEnergy = self.storedEnergy + self.energyProvidedPerTick * self.assignedEnergyLevel
            print(f"{self} stored energy: {self.storedEnergy}")
        else:
            print(f"{self} powering off. stored energy: {self.storedEnergy}")
            self.at_power_off()
            
            self.location.msg_contents(f"{self.name} falters and powers off as it runs out of fuel.")
            pass

    def transfer_energy(self, receiver):
        print(f"{self} transferring energy to {receiver}")
        receiver_power_draw = receiver.energyConsumedPerTickPerLevel * receiver.assignedEnergyLevel

        if self.storedEnergy > self.energyTransferredPerTick:
            amount_to_transfer = self.energyTransferredPerTick

            if receiver_power_draw < amount_to_transfer:
                amount_to_transfer = receiver_power_draw

            self.storedEnergy = self.storedEnergy - amount_to_transfer 

            receiver.storedEnergy = receiver.storedEnergy + amount_to_transfer


    def consume_energy(self):
        print(f"{self} attempting to consume energy")
        if self.powered:
            power_draw = self.energyConsumedPerTickPerLevel * self.assignedEnergyLevel

            if self.storedEnergy > power_draw:
                print(f"{self} consuming energy.")
                self.storedEnergy = self.storedEnergy - power_draw
                self.at_consume_energy()
            else:
                print(f"{self} not enough energy to consume. powering off")
                self.location.msg_contents(f"{self.name} falters as it cannot draw enough power.")
                self.at_power_off()

    # Override in each type of module to do the things.
    def at_consume_energy(self):
        pass

    def at_power_on(self):
        tickerhandler.add(1, self.at_tick)
        self.powered = True
        self.assignedEnergyLevel = 1
        self.location.msg_contents(f"{self} Powered on.")

    def at_power_off(self):
        tickerhandler.remove(1, self.at_tick)
        self.powered = False
        self.assignedEnergyLevel = 0
        self.location.msg_contents(f"{self} Powered off.")

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


