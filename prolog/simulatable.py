from evennia import TICKER_HANDLER as ticker
import evennia
import clingo
import threading
import time

class Simulatable:
    to_simulate = {}
    simulation_thread = None    
    simulation_print = print

    @classmethod
    def program(cls):
        pass

    @classmethod
    def simulate(cls):
        if cls.program() != None:
            print(f"Simulating: {cls}")
            # create controller
            ctl = clingo.Control()

            # Add program
            ctl.add("base", [], cls.program())

            # Add all to_simulate[] terms
            for key,item in cls.to_simulate.items():
                fact = item.to_fact()
                ctl.add("base", [], fact)

            # Ground
            ctl.ground([("base", [])])

            # Solve
            ctl.solve(on_model=cls.update)
            ctl.cleanup()

    @classmethod
    def update(cls, model):
        # Catch solved model, interpret terms into updates for tracked objects
        pass

    @classmethod
    def track(cls, instance):
        cls.to_simulate[instance.id] = instance

        if cls.simulation_thread != None and not cls.simulation_thread.is_alive():
            cls.simulation_thread = None

        if cls.simulation_thread == None:

            def simulation_loop():
                while True:
                    try:
                        start_time = time.time()

                        cls.simulate()

                        elapsed_time = time.time() - start_time
                        sleep_time = max(1 - elapsed_time, 0)

                        time.sleep(sleep_time)

                        if len(list(cls.to_simulate.items())) == 0:
                            return True
                    except Exception as e:
                        print("!!! SIMULATION THREAD EXCEPTION !!!")
                        print(f"{cls}")
                        print(e)
                        cls.simulation_thread = None

            cls.simulation_thread = threading.Thread(target=simulation_loop)
            cls.simulation_thread.setDaemon(True)  # Set as a daemon so it exits when main program exits
            cls.simulation_thread.start()
            

    @classmethod
    def ignore(cls, instance):
        del cls.to_simulate[instance.id]

    def to_fact(self):
        raise Exception("Must be overriden in the base class")
