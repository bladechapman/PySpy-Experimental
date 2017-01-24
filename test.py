from pyspy import observe, ignore, ObservableValue, ObservableFunction

# class Test():
#     def __init__(self):
#         self.test_val = 3
#
#     @observe("test_val")
#     def serialize(self, values=None):
#         print("Test serialize")
#         return {"test": self.test_val}
#
# t = Test()
# t.test_val = 4

t = ObservableValue(2)

def handler():
    print("HANDLED")

handler = observe(t)(handler)

def handler2():
    print("HANDLED 2")

handler = ObservableFunction(handler)
handler2 = observe(handler)(handler2)

def handler3():
    print("HANDLED 3")

handler2 = ObservableFunction(handler2)
handler3 = observe(handler2)(handler3)

print("---")
t.set(4)
