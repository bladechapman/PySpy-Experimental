# PySpy
A rough draft implementation of the observable pattern in Python. These observables can be located within or outside of a class, chained together in a functional manner, allow handlers to attach despite the target being missing, provide both new and old values in a handler, and a few other powerful features. This implementation is experimental and mostly for educational purposes. There are holes in the API and inconsistencies with the behavior. Do NOT use this in any kind of serious project.

## Usage
See test cases and example within the source for more detailed examples.

#### Class-Based Usage
```
from pyspy import *

class MyClass(ContainsObservables):
    @setup
    def __init__(self):
        super().__init__()
        self.value_to_observe = 100

    @observe("value_to_observe", is_class=True)
    def handler(self, old=None, new=None):
        print("observed value has changed:", new["value"])

foo = MyClass()
foo.value_to_observe = 101
```
#### Variable-Based Usage
```
from pyspy import *

value = ObservableValue(100)
def handler(new=None, old=None):
    print("observed value has changed:", new["value"])

handler = observe(value)(handler)
value.set(101)
``` 

