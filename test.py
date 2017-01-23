from pyspy import observe, ignore, Observable

class Test2(Observable):
    def __init__(self):
        self.test_val = 3
        Observable.reveal(self)

    @observe("test_val")
    def serialize(self, values=None):
        print("Test2 serialize")
        return {"test2": self.test_val}

    # @observe("serialize")
    # def secondary(self, values=None):
    #     print("SECONDARY", values)


class Test(Observable):
    def __init__(self):
        self.complex_object = None
        Observable.reveal(self)

    @observe("complex_object")
    def init_complex_object(self, values=None):
        if self.complex_object is not None:
            print("SET")
            observe("complex_object.serialize")(self.serialize2)
            Observable.reveal(self)
        else:
            print("REMOVE")
            # ignore("complex_object.serialize", self.serialize2, self)
            # Observable.reveal(self)

    # @observe()
    def serialize2(self, values=None):
        print("Test serialize")


t1 = Test()
t2 = Test2()
t1.complex_object = t2
t1.complex_object.test_val = 5

# print("SET NONE")
# t1.complex_object = None
# print("SET NONE DONE")
# Observable.reveal(t2)
# t2.test_val = 6
