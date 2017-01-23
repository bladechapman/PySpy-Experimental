from pyspy import observe, ignore, Observable

class Test2(Observable):
    def __init__(self):
        self.test_val = 3
        Observable.reveal(self)

    @observe("test_val")
    def serialize(self, values=None):
        print("Test2 serialize")
        return {"test2": self.test_val}

    @observe("serialize")
    def secondary(self, values=None):
        print("SECONDARY", values)


class Test(Observable):
    def __init__(self):
        self.complex_object = Test2()
        Observable.reveal(self)

    @observe("complex_object")
    def init_complex_object(self, values=None):
        if self.complex_object is not None:
            print("SET")
            observe("complex_object.serialize")(self.serialize2)
            # Observable.reveal(self.complex_object)
            Observable.reveal(self)
        else:
            print("REMOVE")
            ignore("complex_object.serialize")(self.serialize2)
            # Observable.reveal(self.complex_object)
            Observable.reveal(self)

    @observe("complex_object.serialize")
    def serialize2(self, values=None):
        print("Test serialize")


t1 = Test()
# print(t1.serialize2.__observed_attributes)
# print(t1.registered_attributes)
t2 = Test2()
t1.complex_object = t2
t1.complex_object.test_val = 5

# t2 = Test2()
# t2.test_val = 3
# print("FDASFS")
# t2.serialize()

# t2.serialize()
