# PySpy
## Goal: observable python functions. The end intent is that one can declare certain class properties observable via a pyspy decorator. Applications are constructed by linking observables.

## Implementation
- Take the form of a decorator

@observe(self.observed_prop)
def function_to_trigger(self):
    ...


