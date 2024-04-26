from evennia import TICKER_HANDLER as ticker
import evennia
import clingo
import threading
import time
import traceback

class Simulatable:
    to_simulate = {}
    simulation_thread = None    
    simulation_print = print
    failure = False
    last_error = ""

    def program(self):
        pass

    def simulate(self):
        if self.program() != None:
            #print(f"Simulating: {self}")
            # create controller
            ctl = clingo.Control()

            # Add program
            ctl.add("base", [], self.program())

            # Add all to_simulate[] terms
            for key,item in self.to_simulate.items():
                fact = item.to_fact()
                ctl.add("base", [], fact)

            # Ground
            ctl.ground([("base", [])])

            # Solve
            ctl.solve(on_model=self.update)
            ctl.cleanup()

    def update(self, model):
        # Catch solved model, interpret terms into updates for tracked objects
        pass

    def clear_failure(self):
        self.failure = False
        self.last_error = ""

    def track(self, instance):
        self.to_simulate[instance.id] = instance

        if self.simulation_thread != None and not self.simulation_thread.is_alive():
            self.simulation_thread = None

        if self.simulation_thread == None and not self.failure:
            def simulation_loop():
                while True:
                    try:
                        start_time = time.time()

                        self.simulate()

                        elapsed_time = time.time() - start_time
                        sleep_time = max(1 - elapsed_time, 0)

                        time.sleep(sleep_time)

                        if len(list(self.to_simulate.items())) == 0:
                            return True
                    except Exception as e:
                        print("!!! SIMULATION THREAD EXCEPTION !!!")
                        print(f"{self}")
                        print(e)

                        traceback.print_exc()
                        self.failure = True

                        self.simulation_thread = None

            self.simulation_thread = threading.Thread(target=simulation_loop)
            self.simulation_thread.setDaemon(True)  # Set as a daemon so it exits when main program exits
            self.simulation_thread.start()
            

    def ignore(self, instance):
        del self.to_simulate[instance.id]

    def to_fact(self):
        raise Exception("Must be overriden in the base class")
