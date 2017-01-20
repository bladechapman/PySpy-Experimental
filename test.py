from pyspy import observe, Observable

class Test2(Observable):

    test_val4 = 4

    def __init__(self):
        self.test_val3 = 3
        Observable.reveal(self)


class Test(Observable):
    def __init__(self):
        self.test_val = 1
        self.test_val2 = 2
        self.chained_test = Test2()
        Observable.reveal(self)

    @observe("test_val")
    @observe("test_val2")
    @observe("chained_test.test_val3")
    @observe("chained_test.test_val4")
    def test(self):
        print("HANDLER:", \
            self.test_val, \
            self.test_val2,
            self.chained_test.test_val3,
            self.chained_test.test_val4)


t = Test()
t.test_val = 2
t.test_val2 = 3
t.chained_test.test_val3 = 4
t.chained_test.test_val4 = 5
