from evennia.utils import create
from evennia.utils.test_resources import EvenniaTest, EvenniaCommandTest
from unittest.mock import patch, MagicMock

from typeclasses.subsystems.base import Subsystem, DefaultCore, DefaultBattery, DefaultRadar, DefaultEngine, DefaultReactor
from typeclasses.vehicles.base import DefaultSpaceShip
from typeclasses.objects import Object, CmdPilotVehicle, CmdPowerOnVehicle, CmdPilotLaunch, CmdPilotDock, CmdRadarPulse, CmdEngineThrust
from typeclasses.objects import SpaceRoom, SpaceRoomDock

from prolog.hardcodable import Hardcodable, HardcodeProgram

from evennia import TICKER_HANDLER as tickerhandler
import time

class TestSubsystems(EvenniaCommandTest):
    def setUp(self):
        """Called before every test method"""
        super().setUp()

        tickerhandler.add = MagicMock(name='add')
        tickerhandler.remove = MagicMock(name='remove')

        self.default_vehicle = create.create_object( DefaultSpaceShip, key="ship" )
        self.default_vehicle.aiCore = self.char2
        self.char2.move_to(self.default_vehicle)

        self.default_vehicle.move_to(self.room1)


        self.default_core = self.default_vehicle.aiCore
        self.default_core.link_to(self.default_vehicle.search("reactor"))
        self.default_reactor = self.default_core.linkedSubsystems[0]
        self.default_battery = self.default_reactor.linkedSubsystems[0]
        self.default_engine = self.default_battery.linkedSubsystems[0]
        self.default_radar = self.default_battery.linkedSubsystems[1]

        self.call( cmdobj=CmdPilotVehicle(), input_args="ship", caller=self.char2)

        self.space_room = create.create_object( SpaceRoom, key="space_room" )

        self.dock = create.create_object( SpaceRoomDock, key="dock",  )
        self.dock.exit_room = self.space_room

        
        self.room1.newtonian_data["x"] = 20
        self.room1.newtonian_data["y"] = 20

        self.dock.move_to(self.room1)
        self.room1.move_to(self.space_room)

    def test_default_reactor(self):
        self.default_reactor.at_power_off()
        self.assertEqual( self.default_reactor.energyProvidedPerTick, 10 )
        self.assertEqual( self.default_reactor.assignedEnergyLevel, 0 )
        self.assertEqual( self.default_reactor.storedEnergy, 0 )

    def test_default_reactor_energy_generation(self):
        # Hack some fuel in
        self.default_reactor.storedFuel = 100
        # Other systems are draining each tick, so give it some time
        self.default_reactor.at_tick()
        self.default_reactor.at_tick()
        self.default_reactor.at_tick()
        self.default_reactor.at_tick()
        self.default_reactor.at_tick()
        self.default_reactor.at_tick()

        self.assertEqual(self.default_reactor.storedEnergy, 10)

    def test_default_reactor_no_fuel(self):
        self.call( cmdobj=CmdPowerOnVehicle(), input_args="", caller=self.char2)
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
        self.call( cmdobj=CmdPowerOnVehicle(), input_args="", caller=self.char2)

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
        self.call(CmdPowerOnVehicle(), "", caller=self.char2)
        self.call(CmdPilotLaunch(), "", caller=self.char2)
        self.run_normal_tick()
        self.run_normal_tick()
        self.run_normal_tick()
        self.run_normal_tick()
        self.call( cmdobj=CmdRadarPulse(), input_args="" , caller=self.char2)
    
    def test_thrust_north(self):
        self.call(CmdPowerOnVehicle(), "", caller=self.char2)
        self.call(CmdPilotLaunch(), "", caller=self.char2)
        self.run_normal_tick()
        self.run_normal_tick()
        self.run_normal_tick()
        self.run_normal_tick()

        self.call(CmdEngineThrust(), "n", caller=self.char2)
        self.call(CmdEngineThrust(), "e", caller=self.char2)
        self.call(CmdRadarPulse(), input_args="" , caller=self.char2)

        time.sleep(1)
        self.run_normal_tick()
        self.call(CmdEngineThrust(), "w", caller=self.char2)
        self.call(CmdRadarPulse(), input_args="" , caller=self.char2)

        time.sleep(1)
        self.call(CmdEngineThrust(), "w", caller=self.char2)
        self.run_normal_tick()
        self.call(CmdRadarPulse(), input_args="" , caller=self.char2)

        time.sleep(1)
        self.call(CmdEngineThrust(), "e", caller=self.char2)
        self.run_normal_tick()
        self.call(CmdRadarPulse(), input_args="" , caller=self.char2)

        self.call(CmdEngineThrust(), "s", caller=self.char2)
        self.call(CmdEngineThrust(), "s", caller=self.char2)
        self.call(CmdRadarPulse(), input_args="" , caller=self.char2)

        time.sleep(1)
        self.run_normal_tick()
        self.call(CmdRadarPulse(), input_args="" , caller=self.char2)

        time.sleep(1)
        self.run_normal_tick()
        self.call(CmdRadarPulse(), input_args="" , caller=self.char2)

        time.sleep(1)
        self.run_normal_tick()
        
        self.call(CmdRadarPulse(), input_args="" , caller=self.char2)

        time.sleep(1)
        self.run_normal_tick()
        self.call(CmdRadarPulse(), input_args="" , caller=self.char2)

        time.sleep(1)
        self.run_normal_tick()
        self.call(CmdRadarPulse(), input_args="" , caller=self.char2)

        time.sleep(1)
        self.run_normal_tick()
        self.call(CmdRadarPulse(), input_args="" , caller=self.char2)

        time.sleep(1)
        self.run_normal_tick()
        self.call(CmdRadarPulse(), input_args="" , caller=self.char2)

    def items_length(self, incoming_dict):
        return len(list(incoming_dict.items()))

    def test_core_computer_smoke_test(self):
        hc_program = create.create_object( HardcodeProgram, key="smoke_test" )
        hc_program.hardcode_content = "hello(world). #show hello/1. command(\"look\"). #show command/1."
        core = self.default_core
        core.debugging = True

        hc_program.move_to(core)
        self.default_vehicle.chained_power(core, True)

        self.assertEqual(core.load_program("smoke_test"), True)
        self.assertEqual(core.run_program("smoke_test"), True)
        self.assertEqual(self.items_length(core.running_programs), 1)
        self.assertEqual(core.kill_program("smoke_test"), True)
        self.assertEqual(self.items_length(core.running_programs), 0)
        self.assertEqual(core.unload_program("smoke_test"), True)
        self.assertEqual(self.items_length(core.loaded_programs), 0)
        self.assertEqual(core.run_program("smoke_test"), False)
        self.assertEqual(self.items_length(core.running_programs), 0)


        self.assertEqual(len(core.sensors) > 0, True)

        self.call(CmdPilotLaunch(), "", caller=self.char2)
        print(self.call(CmdEngineThrust(), "n", caller=self.char2 ))
        self.run_normal_tick()
        self.run_normal_tick()
        self.run_normal_tick()
        self.run_normal_tick()


        time.sleep(3)

        print(core.view_data_stream())
        self.assertEqual(core.load_program("smoke_test"), True)
        self.assertEqual(core.run_program("smoke_test"), True)

        time.sleep(3)

        print("\n".join(core.logs))

