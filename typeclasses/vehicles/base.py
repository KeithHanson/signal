from evennia import CmdSet, AttributeProperty
from evennia import TICKER_HANDLER as tickerhandler

from typeclasses.objects import Object
from typeclasses.subsystems.base import Subsystem

import evennia


# TODO: Provide new commands at power on and remove them at power off
class Vehicle(Object):
    armor = AttributeProperty(default=0)
    pilot = AttributeProperty(None)

    powered = AttributeProperty(False)
    
    aiCore = AttributeProperty(None)

    def to_fact(self):
        #%   (B, Ix, Iy, IVx, IVy, Fx, Fy, M, T)
        #body(1, 0,  0,  0,   0,   1,  0,  1, 0).
        return f"body({self.id}, {self.newtonian_data['x']}, {self.newtonian_data['y']}, {self.newtonian_data['Vx']}, {self.newtonian_data['Vy']}, {self.newtonian_data['Vx']}, {self.newtonian_data['Fx']}, {self.newtonian_data['Fx']}, 1, 0)."

    def update_prompt(self, caller):
        ship = caller.location

        ship.pilot.msg(prompt=self.get_prompt_text())

    def get_prompt_text(self):
        powered_color = "|g" if self.powered else "|r"
        powered_text = "on" if self.powered else "off"
        sub_texts = []

        for item in self.contents:
            if isinstance(item, Subsystem):
                system_text = item.get_prompt_text()

                sub_texts.append("[" + system_text + "]|n")

        full_subsystems_text = ' '.join(sub_texts)

        position_string = ""
        if self.nattributes.get("pos") != None:
            position_string = f" x:{self.nattributes.pos['x']},y:{self.nattributes.pos['y']}"

        return f"{self.name}{position_string} {powered_color}{powered_text}|n {full_subsystems_text}] >\n"

    def get_display_desc(self, looker, **kwargs):
        if self.powered:
            return self.db.desc + " The vehicle hums quietly, powered and ready for flight. " + "Subsystems: " + str(len(self.aiCore.linkedSubsystems))
        else:
            return self.db.desc + " The vehicle sits silently, powered off, awaiting it's pilot. " + "Subsystems: " + str(len(self.aiCore.linkedSubsystems))

    def at_object_creation(self):
        self.cmdset.add_default('typeclasses.objects.VehicleEntryCmdSet')

        core = evennia.create_object('subsystems.base.DefaultCore', key="stock_core", location=self, aliases=["core"])

        reactor = evennia.create_object('subsystems.base.DefaultReactor', key="stock_reactor", location=self, aliases=["reactor"])
        core.link_to(reactor)

        battery = evennia.create_object('subsystems.base.DefaultBattery', key="stock_battery", location=self, aliases=["battery"])
        reactor.link_to(battery)

        engine = evennia.create_object('subsystems.base.DefaultEngine', key="stock_engine", location=self, aliases=["engine"])
        battery.link_to(engine)

        radar = evennia.create_object('subsystems.base.DefaultRadar', key="stock_radar", location=self, aliases=["radar"])
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

    def chained_power(self, subsys, powerOn):
        if powerOn:
            subsys.at_power_on()
        else:
            subsys.at_power_off()

        for linked in subsys.linkedSubsystems:
            self.chained_power(linked, powerOn)

    def at_power_on(self):
        self.powered = True
        self.pilot.msg("You feel the engines rumble to life. Your HUD begins to boot, and blinking lights spring to life.")

        self.location.msg("You feel a rumble in your chest as {key} powers up and begins levitating.")
        self.chained_power(self.aiCore, True)


    def at_power_off(self):
        self.powered = False
        self.location.msg("As the vehicle powers off, it lands softly on the ground.")
        self.pilot.msg("You feel the vehicle land softly and watch as your subsystems power off.")
        self.chained_power(self.aiCore, False)

    def at_object_delete(self):
        for cur_system in self.contents:
            if cur_system:
                cur_system.location = evennia.settings.DEFAULT_HOME
                cur_system.delete()

        return True

class DefaultSpaceShip(Vehicle):
    pass
