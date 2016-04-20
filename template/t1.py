from DBClient import *


class Test(object):

    def __init__(self):
        self.x = 10

    def set_x(self, x):
        self.x = x

    def get_x(self):
        return self.x

test = Test()