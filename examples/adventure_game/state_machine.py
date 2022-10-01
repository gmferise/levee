from src.levee import Chart, State, Effect, Condition

class Game(Chart):

    class HOME_BEDROOM(State): pass
    class HOME_BATHROOM(State): pass
    class HOME_KITCHEN(State): pass
    class HOME_FRONT_DOOR(State): pass

    diagram = {
        HOME_BEDROOM: {},
        HOME_BATHROOM: {},
        HOME_KITCHEN: {},
        HOME_FRONT_DOOR: {},
    }

if __name__ == '__main__':
    from pdb import set_trace
    set_trace()