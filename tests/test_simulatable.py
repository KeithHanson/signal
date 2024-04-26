from prolog.simulatable import Simulatable

from evennia.utils import create
from evennia.utils.test_resources import EvenniaTest, EvenniaCommandTest
from unittest.mock import patch, MagicMock
from typeclasses.objects import Object

import time

class TestSimulatable(EvenniaCommandTest):
    def setUp(self):
        """Called before every test method"""
        super().setUp()

    def test_smoke_test(self):
        class MySimulatable(Object, Simulatable):
            key="my_sim"
            color="red"
            opposite=None

            def program(self):
                return """
                color(blue) :- opposite(red).
                opposite(red) :- color(blue).

                color(red) :- opposite(blue).
                opposite(blue) :- color(red).

                color(green) :- opposite(green).
                opposite(green) :- color(green).

                #show opposite/1.
                """

            def to_fact(self):
                return f"color({self.color})." 

            def update(self, model):
                symbol = str(model.symbols(shown=True)[0])
                key,item = list(self.to_simulate.items())[0]

                self.opposite = symbol.split("(")[1].replace(")", "")

        sim = MySimulatable()
        sim.track(sim)
        time.sleep(1)
        self.assertEqual(sim.opposite, "blue")
