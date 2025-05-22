# Levee
Create state machines with a visually pleasing syntax in Python

Remember, keep your Levee [DRY!](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)

## Example Usage

For more examples of what you can do, read the [tests](https://github.com/gmferise/levee/tree/main/tests/levee)

```python
from levee import Chart, State, Condition, Effect

class FlowChart(Chart):
    class ALPHA(State): pass
    class BETA(State): pass
    class GAMMA(State): pass

    class Sometimes(Condition):

        def eval(self, sometimes):
            return sometimes
    
    class Maybe(Condition):

        def eval(self, maybe):
            # Return a string to block the transition with a reason
            return maybe if maybe else 'I guess not'

    class PrintWhatever(Effect):

        def exec(self, whatever):
            # Parameter names in the definition of Condition.eval/Effect.exec will become
            # required named arguments for Chart.to/Chart.can/Chart.choices
            print(whatever)
    
    class SayHello(Effect):
        
        def exec(self):
            print('Hello!')

    chart = {
        ALPHA: {
            BETA (Sometimes) [PrintWhatever]: ...,
            GAMMA (Sometimes | Maybe) [SayHello]: ...,
        },
        BETA: {
            ALPHA (Sometimes & Maybe) [PrintWhatever + PrintWhatever]: ...,
        },
        GAMMA: {
            ALPHA (~Maybe) [PrintWhatever + SayHello]: ...,
        }
    }

def main():
    data = { 'state': None }
    chart = FlowChart(data)
    print(chart.state, chart.choices(sometimes=True, maybe=False, whatever='whatever'))
    chart.to(FlowChart.BETA, sometimes=True, whatever='Whatever Once')
    chart.to(FlowChart.ALPHA, sometimes=True, maybe=True, whatever='Whatever Twice')
    if chart.can(FlowChart.GAMMA, sometimes=False, maybe=True):
      chart.to(FlowChart.GAMMA, sometimes=False, maybe=True)
    chart.to(FlowChart.ALPHA, maybe=False, whatever='Goodbye!')

```