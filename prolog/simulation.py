import clingo

def read_pl_file(filename):
    """Reads a .pl file and returns its content as a string."""
    with open(filename, 'r') as file:
        return file.read()

def update_model(model, new_terms):
    """Updates the Clingo model with new terms."""
    for term in new_terms:
        model.add((), term)

def solve_simulation(filename, new_terms):
    """Solves the simulation using Clingo."""
    # Create a Control object
    ctl = clingo.Control()

    # Read the contents of the .pl file
    program = read_pl_file(filename)

    # Add the program to the control
    ctl.add('base', [], program)

    # Ground the program
    ctl.ground([("base", [])])

    # Solve the program
    ctl.solve()

    # Retrieve the model
    model = ctl.get_model()

    # Update the model with new terms
    update_model(model, new_terms)

    # Solve the updated program
    ctl.solve()

    # Retrieve and print the updated model
    updated_model = ctl.get_model()
    #print("Updated Model:")
    for atom in updated_model.symbols(shown=True):
        #print(atom)

# Example usage
if __name__ == "__main__":
    filename = "moving_bodies_simulation.pl"
    new_terms = ["new_term(a, b, c).", "new_rule(X) :- condition(X)."]
    solve_simulation(filename, new_terms)
