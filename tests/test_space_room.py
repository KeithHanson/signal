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
        
        self.room1.newtonian_data["x"] = 20
        self.room1.newtonian_data["y"] = 20

        self.room1.move_to(self.space_room)

        self.ship.move_to(self.room1)
        self.dock.move_to(self.room1)
        self.char1.move_to(self.room1)

        self.call( cmdobj=CmdPilotVehicle(), input_args="ship")

        self.test_map = """
15 | . . . . . . . . . . . 
16 | . . . . . . . . . . . 
17 | . . . . . . . . . . . 
18 | . . . . . . . . . . . 
19 | . . . . . . . . . . . 
20 | . . . . . @ . . . . . 
21 | . . . . . . . . . . . 
22 | . . . . . . . . . . . 
23 | . . . . . . . . . . . 
24 | . . . . . . . . . . . 
25 | . . . . . . . . . . . 
    ----------------------
             x:20
"""

    def test_basic_creation(self):
        self.assertEqual( self.ship.name, "ship" )
        self.assertEqual( self.space_room.name, "space_room" )
        self.assertEqual( self.dock.name, "dock" )

    def test_launch(self):
        self.call(CmdPilotLaunch(), "")
        
        self.assertEqual(self.ship.location, self.space_room)

        contents = self.space_room.contents_get()

        self.assertEqual(self.room1.newtonian_data["x"], 20)
        self.assertEqual(self.room1.newtonian_data["y"], 20)
        self.assertEqual(self.room1.newtonian_data, self.ship.newtonian_data)

        self.call(CmdPilotLook(), "")

    def test_spaceroom_dimensions(self):
        self.assertEqual(self.space_room.width, 1000)
        self.assertEqual(self.space_room.height, 1000)

    def test_spaceroom_map(self):
        self.maxDiff = None
        self.call(CmdPilotLaunch(), "")

        self.assertEqual(self.ship.location, self.space_room)

        caller = self.char1
        self.rendered_map = self.space_room.render_map(caller)

        for row in range(0, len(self.test_map.split("\n"))):
            test_string = self.test_map.split("\n")[row]
            rendered_string = self.rendered_map.split("\n")[row]

            self.assertEqual(test_string, rendered_string)

        print(self.rendered_map)
