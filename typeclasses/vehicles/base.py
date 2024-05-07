from evennia import CmdSet, AttributeProperty
from evennia import TICKER_HANDLER as tickerhandler

from typeclasses.objects import Object
from typeclasses.subsystems.base import Subsystem

import evennia

from textwrap import dedent

# TODO: Provide new commands at power on and remove them at power off
class Vehicle(Object):
    armor = AttributeProperty(default=0)
    powered = AttributeProperty(False)
    
    aiCore = AttributeProperty(None)

    def to_fact(self):
        return dedent(f"""
        %    (B, Ix, Iy, IVx, IVy, Fx, Fy, M, T)
        %body(1, 0,  0,  0,   0,   1,  0,  1, 0).
        body({self.id}, {self.newtonian_data['x']}, {self.newtonian_data['y']}, {self.newtonian_data['Vx']}, {self.newtonian_data['Vy']}, {self.newtonian_data['Fx']}, {self.newtonian_data['Fy']}, 1, 0).
        """)

    def update_prompt(self, caller):
        if self.aiCore:
            self.aiCore.msg(prompt=self.get_prompt_text())

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
            return (str(self.db.desc) + " " if self.db.desc != None else "") + "The vehicle hums quietly, powered and ready for flight."
        else:
            return (str(self.db.desc) + " " if self.db.desc != None else "") + "The vehicle sits silently, powered off."

    def at_object_creation(self):
        # Build and link everything but a core (which will be the player)
        reactor = evennia.create_object('subsystems.base.DefaultReactor', key="stock_reactor", location=self, aliases=["reactor"])

        battery = evennia.create_object('subsystems.base.DefaultBattery', key="stock_battery", location=self, aliases=["battery"])
        reactor.link_to(battery)

        engine = evennia.create_object('subsystems.base.DefaultEngine', key="stock_engine", location=self, aliases=["engine"])
        battery.link_to(engine)

        radar = evennia.create_object('subsystems.base.DefaultRadar', key="stock_radar", location=self, aliases=["radar"])
        battery.link_to(radar)

        self.save()

        self.cmdset.add("typeclasses.objects.VehiclePilotingCmdSet", persistent=True)

    def chained_power(self, subsys, powerOn):
        if subsys:
            if powerOn:
                subsys.at_power_on()
            else:
                subsys.at_power_off()

            for linked in subsys.linkedSubsystems:
                self.chained_power(linked, powerOn)

    def at_power_on(self):
        self.powered = True
        self.aiCore.msg("Ship power sequence activated.")

        self.chained_power(self.aiCore, True)


    def at_power_off(self):
        self.powered = False
        self.chained_power(self.aiCore, False)

    def at_object_delete(self):
        for cur_system in self.contents:
            if cur_system:
                cur_system.location = evennia.settings.DEFAULT_HOME
                cur_system.delete()

        return True

class DefaultSpaceShip(Vehicle):
    pass
