from evennia.utils import create
from evennia.utils.test_resources import EvenniaTest, EvenniaCommandTest
from unittest.mock import patch, MagicMock

from typeclasses.vehicles.base import DefaultSpaceShip
from typeclasses.objects import Object, SpaceRoom, SpaceRoomDock, CmdPilotLaunch, CmdPilotVehicle, CmdPilotLook

class TestSpaceRoom(EvenniaCommandTest):
    def setUp(self):
        super().setUp()

        self.ship = create.create_object( DefaultSpaceShip, key="ship" )

        self.space_room = create.create_object( SpaceRoom, key="space_room" )

        self.dock = create.create_object( SpaceRoomDock, key="dock",  )
        self.dock.exit_room = self.space_room
        
        self.room1.nattributes.pos = {"x": 20, "y":20}
        self.room1.move_to(self.space_room)


        self.ship.move_to(self.room1)
        self.dock.move_to(self.room1)
        self.char1.move_to(self.room1)

        self.call( cmdobj=CmdPilotVehicle(), input_args="ship")

    def test_basic_creation(self):
        self.assertEqual( self.ship.name, "ship" )
        self.assertEqual( self.space_room.name, "space_room" )
        self.assertEqual( self.dock.name, "dock" )

    def test_launch(self):
        print(self.call(CmdPilotLaunch(), ""))
        
        self.assertEqual(self.ship.location, self.space_room)

        contents = self.space_room.contents_get()

        self.assertEqual(self.room1.nattributes.pos["x"], 20)
        self.assertEqual(self.room1.nattributes.pos["y"], 20)
        self.assertEqual(self.room1.nattributes.pos, self.ship.nattributes.pos)

        print(self.ship.nattributes.pos) 
        print(self.call(CmdPilotLook(), ""))
