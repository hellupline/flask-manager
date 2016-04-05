from collections import OrderedDict
from functools import partial


class ActionSet(OrderedDict):
    def register(self, name, func=None):
        if func is None:
            return partial(self.register, name)
        self[name] = func
        return func
