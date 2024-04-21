from evennia import TICKER_HANDLER as ticker
import evennia

import clingo

class Simulatable:
    to_simulate = []

    @classmethod
    def program(cls):
        pass

    @classmethod
    def simulate(cls):
        # create controller
        ctl = clingo.Control()

        # Add program
        ctl.add("base", [], cls.program())

        # Add all to_simulate[] terms
        for item in cls.to_simulate:
            fact = item.to_fact()
            ctl.add("base", [], fact)

        # Ground
        ctl.ground([("base", [])])

        # Solve
        ctl.solve(on_model=cls.update)
        ctl.cleanup()
        pass

    @classmethod
    def update(cls, model):
        # Catch solved model, interpret terms into updates for tracked objects
        pass

    @classmethod
    def track(cls, instance):
        cls.to_simulate.append(instance)

    @classmethod
    def ignore(cls, instance):
        cls.to_simulate.remove(instance)

    def to_fact(self):
        raise Exception("Must be overriden in the base class")


