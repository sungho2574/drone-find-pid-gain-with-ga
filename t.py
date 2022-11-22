class A:
    def __init__(self) -> None:
        self.a = C()
        self.s = self.B(self.a)
        print(self.a.b)
    
    class B:
        def __init__(self, a) -> None:
            a.b = 9
            # a.setb(7)


class C:
    def __init__(self) -> None:
        self.a = 1
        self.b = 2
    
    def setb (self, n):
        self.b = n

test = A()