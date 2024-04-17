from evennia import Command, CmdSet, CmdSet, AttributeProperty
from .base import Subsystem

class DefaultReactor(Subsystem):
    energyProvidedPerTick = AttributeProperty(1)

    def at_object_creation(self):
        self.name = "Stock Reactor"
