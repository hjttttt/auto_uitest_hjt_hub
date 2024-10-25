class A:

    @classmethod
    def f1(cls):
        print('f1')

    def f2(self):
        print('f2')


if __name__ == '__main__':
    a = A()

    a.f1()
    a.f2()
