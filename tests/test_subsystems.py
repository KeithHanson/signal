from evennia.utils import create
from evennia.utils.test_resources import EvenniaTest
from unittest.mock import patch, MagicMock

from typeclasses.subsystems.base import Subsystem, DefaultCore, DefaultBattery, DefaultRadar, DefaultEngine
from typeclasses.subsystems.reactors import DefaultReactor
from typeclasses.objects import Object

from evennia import TICKER_HANDLER as tickerhandler

class TestSubsystems(EvenniaTest):
    def setUp(self):
        """Called before every test method"""
        super().setUp()

        tickerhandler.add = MagicMock(name='add')
        tickerhandler.remove = MagicMock(name='remove')

        self.basic_room = create.create_object( Object, key="room" )

        self.base_subsystem = create.create_object( Subsystem, key="base_subsystem" )

        self.default_core = create.create_object ( DefaultCore, key="core" )

        self.default_reactor = create.create_object( DefaultReactor, key="reactor" )

        self.default_battery = create.create_object( DefaultBattery, key="battery" )

        self.default_engine = create.create_object( DefaultEngine, key="engine" )

        self.default_radar = create.create_object( DefaultRadar, key="radar" )

        self.default_core.move_to(self.basic_room)
        self.default_reactor.move_to(self.basic_room)
        self.default_battery.move_to(self.basic_room)
        self.default_engine.move_to(self.basic_room)
        self.default_radar.move_to(self.basic_room)

    def test_attribute_properties(self):
        self.assertEqual(self.base_subsystem.HUDname, "subname")

    def test_default_reactor(self):
        self.assertEqual(self.default_reactor.energyProvidedPerTick, 1)

    def test_default_reactor_energy_generation(self):
        self.assertEqual( self.default_reactor.energyProvidedPerTick, 1 )
        self.assertEqual( self.default_reactor.assignedEnergyLevel, 0 )
        self.assertEqual( self.default_reactor.storedEnergy, 0 )

        # Hack the assignedEnergyLevel
        self.default_reactor.assignedEnergyLevel = 1

        # Hack some fuel in
        self.default_reactor.storedFuel = 100
        self.default_reactor.at_tick()

        self.assertEqual(self.default_reactor.storedEnergy, 1)

    def test_default_reactor_no_fuel(self):
        # submodules need a parent
        self.default_reactor.move_to(self.basic_room)

        #power up
        self.default_reactor.at_power_on()

        self.assertEqual(self.default_reactor.powered, True)
        self.assertEqual(self.default_reactor.assignedEnergyLevel, 1)

        # tick
        self.default_reactor.at_tick()

        # should be powered off without fuel.
        self.assertEqual(self.default_reactor.powered, False)

    def link_all_defaults(self):
        self.default_core.link_to(self.default_reactor)

        self.default_reactor.link_to(self.default_battery)

        self.default_battery.link_to(self.default_engine)
        self.default_battery.link_to(self.default_radar)

    def power_all_on(self):
        # Hack some fuel in
        self.default_reactor.fuelConsumedPerTickPerLevel = 1
        self.default_reactor.storedFuel = 100

        self.default_reactor.energyProvidedPerTick = 10
        self.default_reactor.energyTransferredPerTick = 10

        self.default_battery.energyTransferredPerTick = 5

        self.default_core.at_power_on()

        self.default_reactor.at_power_on()

        self.default_battery.at_power_on()

        self.default_engine.at_power_on()

        self.default_radar.at_power_on()


    def test_linking(self):
        self.link_all_defaults()
        self.assertEqual(self.default_core.linkedSubsystems, [self.default_reactor])
        self.assertEqual(self.default_reactor.linkedSubsystems, [self.default_battery])
        self.assertEqual(self.default_battery.linkedSubsystems, [self.default_engine, self.default_radar])

    def test_linked_ticks(self):
        self.link_all_defaults()
        self.power_all_on()

        # simulate the ticks
        self.default_core.at_tick()
        self.default_reactor.at_tick()

        self.assertEqual(self.default_battery.storedEnergy, 10)

        self.default_battery.at_tick()

        self.assertEqual(self.default_battery.storedEnergy, 0)
        self.assertEqual(self.default_engine.storedEnergy, 5)
        self.assertEqual(self.default_radar.storedEnergy, 5)

        self.default_engine.at_tick()
        self.assertEqual(self.default_engine.storedEnergy, 4)

        self.default_radar.at_tick()
        self.assertEqual(self.default_radar.storedEnergy, 4)

        #simulate the next ones
        self.default_core.at_tick()
        self.default_reactor.at_tick()
        self.assertEqual(self.default_battery.storedEnergy, 10)

        self.default_battery.at_tick()
        self.assertEqual(self.default_battery.storedEnergy, 0)
        self.assertEqual(self.default_engine.storedEnergy, 9)
        self.assertEqual(self.default_radar.storedEnergy, 9)

        self.default_engine.at_tick()
        self.assertEqual(self.default_engine.storedEnergy, 8)
        self.default_radar.at_tick()
        self.assertEqual(self.default_radar.storedEnergy, 8)
