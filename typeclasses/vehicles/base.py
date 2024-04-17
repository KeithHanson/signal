from evennia.objects.objects import DefaultObject
from evennia import Command, CmdSet, CmdSet, AttributeProperty
from evennia import TICKER_HANDLER as tickerhandler

# TODO: Provide new commands at power on and remove them at power off
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
