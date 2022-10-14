from sys import path; path.append('src') # Remove me
from levee import Chart, State, Condition, Effect
from random import random

def main():
    obj = { 'state': None }
    chart = Example(obj, 'state', is_key=True)
    from pdb import set_trace; set_trace()

def chance(percent: float):
    return random() < percent / 100

class Example(Chart):

    chart = {}

if __name__ == '__main__':
    main()