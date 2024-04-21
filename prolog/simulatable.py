from evennia import TICKER_HANDLER as ticker
import evennia

import clingo

class Simulatable:
    to_simulate = []

    def program():
        pass

    def simulate():
        pass

    def update(model):
        pass

    def track(instance):
        to_simulate.append(instance)

    def ignore(instance):
        to_simulate.remove(instance)

    def to_fact(self):
        class_name = type(self).__name__
        attributes = obj.attributes.all()

        for attribute in attributes:
