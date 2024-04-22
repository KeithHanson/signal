from prolog.simulatable import Simulatable

from evennia.utils import create
from evennia.utils.test_resources import EvenniaTest, EvenniaCommandTest
from unittest.mock import patch, MagicMock
from typeclasses.objects import Object

class TestSimulatable(EvenniaCommandTest):
    def setUp(self):
        """Called before every test method"""
        super().setUp()

    def test_smoke_test(self):
        class MySimulatable(Object, Simulatable):
            key="my_sim"
            color="red"
            opposite=None

            @classmethod
            def program(cls):
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

            @classmethod
            def update(cls, model):
                symbol = str(model.symbols(shown=True)[0])
                key,item = list(cls.to_simulate.items())[0]

                item.opposite = symbol.split("(")[1].replace(")", "")

        sim = MySimulatable()
        MySimulatable.track(sim)
        MySimulatable.simulate()
        self.assertEqual(sim.opposite, "blue")
