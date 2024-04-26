from evennia.utils import create
from evennia.utils.test_resources import EvenniaTest, EvenniaCommandTest
from unittest.mock import patch, MagicMock

from typeclasses.subsystems.base import Subsystem, DefaultCore, DefaultBattery, DefaultRadar, DefaultEngine, DefaultReactor
from typeclasses.vehicles.base import DefaultSpaceShip
from typeclasses.objects import Object, CmdPilotVehicle, CmdPowerOnVehicle, CmdPilotLaunch, CmdPilotDock, CmdRadarPulse, CmdEngineThrust
from typeclasses.objects import SpaceRoom, SpaceRoomDock

from evennia import TICKER_HANDLER as tickerhandler
import time

class TestSubsystems(EvenniaCommandTest):
    def setUp(self):
        """Called before every test method"""
        super().setUp()

        tickerhandler.add = MagicMock(name='add')
        tickerhandler.remove = MagicMock(name='remove')

        self.default_vehicle = create.create_object( DefaultSpaceShip, key="ship" )
        self.default_vehicle.move_to(self.room1)

        self.char1.move_to(self.room1)

        self.default_core = self.default_vehicle.aiCore
        self.default_reactor = self.default_core.linkedSubsystems[0]
        self.default_battery = self.default_reactor.linkedSubsystems[0]
        self.default_engine = self.default_battery.linkedSubsystems[0]
        self.default_radar = self.default_battery.linkedSubsystems[1]

        self.call( cmdobj=CmdPilotVehicle(), input_args="ship")

        self.space_room = create.create_object( SpaceRoom, key="space_room" )

        self.dock = create.create_object( SpaceRoomDock, key="dock",  )
        self.dock.exit_room = self.space_room

        
        self.room1.newtonian_data["x"] = 20
        self.room1.newtonian_data["y"] = 20

        self.dock.move_to(self.room1)
        self.room1.move_to(self.space_room)

    def test_default_reactor(self):
        self.assertEqual( self.default_reactor.energyProvidedPerTick, 10 )
        self.assertEqual( self.default_reactor.assignedEnergyLevel, 0 )
        self.assertEqual( self.default_reactor.storedEnergy, 0 )

    def test_default_reactor_energy_generation(self):
        # Hack some fuel in
        self.default_reactor.storedFuel = 100
        self.default_reactor.at_tick()

        self.assertEqual(self.default_reactor.storedEnergy, 10)

    def test_default_reactor_no_fuel(self):
        self.call( cmdobj=CmdPowerOnVehicle(), input_args="")
        #power up
        self.default_reactor.storedFuel = 1
        self.assertEqual(self.default_reactor.powered, True)
        self.assertEqual(self.default_reactor.assignedEnergyLevel, 1)

        # tick
        self.default_reactor.at_tick()
        self.default_reactor.at_tick()

        # should be powered off without fuel.
        self.assertEqual(self.default_reactor.powered, False)

    def test_linking(self):
        self.assertEqual(self.default_core.linkedSubsystems, [self.default_reactor])
        self.assertEqual(self.default_reactor.linkedSubsystems, [self.default_battery])
        self.assertEqual(self.default_battery.linkedSubsystems, [self.default_engine, self.default_radar])

    def test_linked_ticks(self):
        self.call( cmdobj=CmdPowerOnVehicle(), input_args="")

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

    def run_normal_tick(self):
        # simulate the ticks
        self.default_core.at_tick()
        self.default_reactor.at_tick()
        self.default_battery.at_tick()
        self.default_engine.at_tick()
        self.default_radar.at_tick()

    def test_radar(self):
        # for now, just make sure it doesn't fail
        self.call(CmdPowerOnVehicle(), "")
        self.call(CmdPilotLaunch(), "")
        self.run_normal_tick()
        self.run_normal_tick()
        self.run_normal_tick()
        self.run_normal_tick()
        self.call( cmdobj=CmdRadarPulse(), input_args="" )
    
    def test_thrust_north(self):
        self.call(CmdPowerOnVehicle(), "")
        self.call(CmdPilotLaunch(), "")
        self.run_normal_tick()
        self.run_normal_tick()
        self.run_normal_tick()
        self.run_normal_tick()

        self.call(CmdEngineThrust(), "n")
        self.call(CmdEngineThrust(), "e")
        self.call(CmdRadarPulse(), input_args="" )

        time.sleep(1)
        self.run_normal_tick()
        self.call(CmdEngineThrust(), "w")
        self.call(CmdRadarPulse(), input_args="" )

        time.sleep(1)
        self.call(CmdEngineThrust(), "w")
        self.run_normal_tick()
        self.call(CmdRadarPulse(), input_args="" )

        time.sleep(1)
        self.call(CmdEngineThrust(), "e")
        self.run_normal_tick()
        self.call(CmdRadarPulse(), input_args="" )

        self.call(CmdEngineThrust(), "s")
        self.call(CmdEngineThrust(), "s")
        self.call(CmdRadarPulse(), input_args="" )

        time.sleep(1)
        self.run_normal_tick()
        self.call(CmdRadarPulse(), input_args="" )

        time.sleep(1)
        self.run_normal_tick()
        self.call(CmdRadarPulse(), input_args="" )

        time.sleep(1)
        self.run_normal_tick()
        
        self.call(CmdRadarPulse(), input_args="" )

        time.sleep(1)
        self.run_normal_tick()
        self.call(CmdRadarPulse(), input_args="" )

        time.sleep(1)
        self.run_normal_tick()
        self.call(CmdRadarPulse(), input_args="" )

        time.sleep(1)
        self.run_normal_tick()
        self.call(CmdRadarPulse(), input_args="" )

        time.sleep(1)
        self.run_normal_tick()
        self.call(CmdRadarPulse(), input_args="" )
