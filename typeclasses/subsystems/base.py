from evennia import Command, CmdSet, CmdSet, AttributeProperty
from evennia import TICKER_HANDLER as tickerhandler
from evennia import utils

from ..characters import Character

from ..objects import Object

from prolog.hardcodable import Hardcodable, HardcodeProgram

from textwrap import dedent
import random

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

    def at_init(self):
        self.at_power_on()

    def status(self):
        pass

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

        if self.provides_cmdset_named != None:
            self.cmdset.remove(self.provides_cmdset_named)
            self.cmdset.add(self.provides_cmdset_named)

        if isinstance(self, Hardcodable): 
            for item in self.location.contents:
                if hasattr(item, "to_fact"):
                    self.add_sensor(item)

    def at_power_off(self):
        try:
            tickerhandler.remove(1, self.at_tick)

            if self.provides_cmdset_named != None:
                self.cmdset.delete(self.provides_cmdset_named)

        except Exception as e:
            pass

        self.powered = False
        self.assignedEnergyLevel = 0
        self.storedEnergy = 0

class DefaultEngine(Subsystem):
    energyCapacity = AttributeProperty(default=10)
    energyConsumedPerTickPerLevel = AttributeProperty(default=1)
    thrustOutputPerLevel = AttributeProperty(default=1)
    provides_cmdset_named = "typeclasses.objects.EngineCmdSet"
    name = "Stock Engine"
    HUDname = "engine"

    def to_fact(self):
        if self.powered:
            return dedent(f"""
            % Engine Facts
            % engine(HUDname, thrustOutputPerLevel, energyConsumedPerTickPerLevel, energyCapacity, storedEnergy).
            engine({self.HUDname}, {self.thrustOutputPerLevel}, {self.energyConsumedPerTickPerLevel}, {self.energyCapacity}, {self.storedEnergy}).
            """)
        else:
            return "engine(off)."

    def status(self):
        if self.powered:
            forcex = self.location.newtonian_data["Fx"]
            forcey = self.location.newtonian_data["Fy"]

            velocx = self.location.newtonian_data["Vx"]
            velocy = self.location.newtonian_data["Vy"]

            if velocx != 0 or velocy != 0:
                return f"eng:F(x:{forcex},y:{forcey}),V(x:{velocx},y:{velocy})"
            else:
                return f"eng:idle|n"
        else:
            return "eng:off"

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
    provides_cmdset_named = "commands.core.CoreCmdSet"

    def update_status(self):
        ship = self.location
        # ignore args

        if not hasattr(ship, "powered"):
            self.msg(prompt="|rCRITICAL |RFAILURE - CORE !|cDETACHED|R! - KERNEL |bPANIC|R\n(panic)> ")
            return

        if hasattr(ship, "powered") and ship.powered:
            ship = f"|cloc({self.location.location} #{self.location.location.id})|n"
        else:
            if not hasattr(ship, "powered"):
                ship = f"|rDISCONNECTED"
            else:
                ship = f"|rship:off|n"

        tab = "\t" 
        pos = f" || |bpos(x:{self.location.newtonian_data['x']},y:{self.location.newtonian_data['y']})|n"

        sensors = f" || |mavail sensors({len(self.sensors)})|n"

        sensor_colors = ['|g', '|y', '|b', '|m', '|c', '|w', '|x', '|r']
        sensor_statuses = [] 

        for index, sensor in enumerate(self.sensors):
            status = sensor.status()
            if status:
                sensor_statuses.append( f"{sensor_colors[index]}{status}|n" )

        line1 = "\n" + f"|n{ship}{pos}{sensors}|n"
        line2 = "\n" + ' || '.join(sensor_statuses)
        line3 = "\n|r(root) #> "
        
        self.msg(prompt=line1 + line2 + line3)


    def login_ascii_art(self):
        return dedent("""|c
                      ,-.         0      1
             / \\  `.  __..-,O      0      1
            :   \\ --''_..-'.'       1      0
            |    . .-' `. '.          0      1
            :     .     .`.'           1     0
             \     `.  /  ..           0     1
              \      `.   ' .          0     0
               `,       `.   \\        1     0
              ,:,`.        `-.\\     1     1
             '.:: ``-...__..-`     0     0
              :  :
              :__:
        """)

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
        self.msg(self.login_ascii_art())

        offset = random.uniform(0.0, 0.5)

        boot_msgs = []

        boot_msgs.append("BIOS-e820: [mem 0x0000000000000000-0x000000000009ffff] usable")
        boot_msgs.append("BIOS-e820: [mem 0x00000000000a0000-0x00000000000fffff] reserved")
        boot_msgs.append("BIOS-e820: [mem 0x0000000000100000-0x0000000018ffffff] usable")
        boot_msgs.append("BIOS-e820: [mem 0x00000000fc000000-0x00000000fc00803f] ACPI data")
        boot_msgs.append("BIOS-e820: [mem 0x00000000feff8000-0x00000000feffffff] reserved")
        boot_msgs.append("last_pfn = 0x19000 max_arch_pfn = 0x400000000")
        boot_msgs.append("RAMDISK: [mem 0x05001000-0x0614cfff]")
        boot_msgs.append("ACPI: RSDP 0x00000000FC008000 000024 (v02 Xen   )")
        boot_msgs.append("ACPI: XSDT 0x00000000FC007F60 000034 (v01 Xen    HVM      00000000 HVML 00000000)")
        boot_msgs.append("ACPI: FACP 0x00000000FC007D60 00010C (v05 Xen    HVM      00000000 HVML 00000000)")
        boot_msgs.append("ACPI: DSDT 0x00000000FC001040 006C9B (v05 Xen    HVM      00000000 INTL 20220331)")
        boot_msgs.append("ACPI: FACS 0x00000000FC001000 000040")
        boot_msgs.append("ACPI: Reserving FACS table memory at [mem 0xfc001000-0xfc00103f]")
        boot_msgs.append("BIOS complete. Booting OS....")

        boot_msgs.append("|m[0.000] |gSignal|yOS |bInitializing... ")
        boot_msgs.append("|m[0.023] |gSignal|yOS |bInitializing... \t\t\t\t|g[OK]")
        
        boot_msgs.append("|m[0.490] |yConnecting basic sentience interface...")
        boot_msgs.append("|m[0.570] |yConnecting basic sentience interface... \t\t|g[OK]")

        boot_msgs.append("|m[1.102] |yBootstrapping quantum entanglement...")
        boot_msgs.append("|m[1.229] |yBootstrapping quantum entanglement... \t\t\t|g[OK]")

        boot_msgs.append("|m[1.854] |yConnecting available sensors to sentience...")
        boot_msgs.append("|m[2.107] |yConnecting available sensors to sentience... \t\t|g[OK]")

        boot_msgs.append("|m[2.301] |yFinal diagnostic tests...")
        boot_msgs.append("|m[2.709] |yFinal diagnostic tests... \t\t\t\t|g[OK]")
        boot_msgs.append("")
        boot_msgs.append("|m[2.805] |rCore |gReady for Sentient Control.")

        for message in boot_msgs:
            utils.delay(offset, self.msg, message)
            offset += random.uniform(0.0, 0.5)
        
        utils.delay(offset, self.update_status)

    def at_power_off(self):
        pass

    def at_init(self):
        self.at_power_on()

    def execute_command(self, command):
        if self.location.aiCore:
            self.location.aiCore.execute_cmd(command)

    def status(self):
        if self.failure:
            return f"core:|rERR"
        else:
            return f"core:Load({len(self.loaded_programs)}),Run({len(self.running_programs)})"

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
        if self.powered:
            return dedent(f"""
            % Reactor Facts
            % reactor(HUDname, energyProvidedPerTick, energyTransferredPerTick, EnergyConsumedPerTickPerLevel, fuelConsumedPerTickPerLevel, storedFuel, energyCapacity, storedEnergy).
            reactor({self.HUDname}, {self.energyProvidedPerTick}, {self.energyTransferredPerTick}, {self.energyConsumedPerTickPerLevel}, {self.fuelConsumedPerTickPerLevel}, {self.storedFuel}, {self.energyCapacity}, {self.storedEnergy}).
            """)
        else:
            return "reactor(off)."

    def status(self):
        if self.powered:
            return f"react:F({self.storedFuel})"
        else:
            return "react:off"

class DefaultBattery(Subsystem):
    name = "Stock Battery"
    HUDname = "battery"
    energyCapacity = AttributeProperty(default=30)
    energyConsumedPerTickPerLevel = AttributeProperty(default=0)
    energyTransferredPerTick = AttributeProperty(default=5)

    def to_fact(self):
        if self.powered:
            return dedent(f"""
            %Battery Facts
            %battery(HUDname, energyTransferredPerTick, energyCapacity, storedEnergy).
            battery({self.HUDname}, {self.energyTransferredPerTick}, {self.energyCapacity}, {self.storedEnergy}).
            """)
        else:
            return "battery(off)."

    def status(self):
        if self.powered:
            return f"bat:E({self.storedEnergy})"
        else:
            return "bat:off"

class DefaultRadar(Subsystem):
    energyCapacity = AttributeProperty(default=10)
    energyConsumedPerTickPerLevel = AttributeProperty(default=1)
    name = "Stock Radar"
    HUDname = "radar"
    provides_cmdset_named = "typeclasses.objects.RadarCmdSet"

    def to_fact(self):
        if self.powered:
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
        else:
            return "radar(off)."

    def pulse(self, caller, space_room):
        power_draw = self.energyConsumedPerTickPerLevel * self.assignedEnergyLevel

        if self.storedEnergy >= power_draw:
            self.storedEnergy -= power_draw
            # Basic implementation, render the map perfectly from the space_room
            caller.msg("")
            caller.msg(space_room.render_map(caller))
            caller.msg("|GRadar pulse executed successfully.")

        else:
            caller.msg(f"|rError: Not enough energy. |gStored: {self.storedEnergy} |yNeeded: {power_draw}")

    def detected_objects(self):
        return []

    def last_pulse(self):
        return (-1,-1)

    def status(self):
        if self.powered:
            return f"rad:Count({len(self.detected_objects())})"
        else:
            return "rad:off"
