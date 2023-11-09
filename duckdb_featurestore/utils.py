class NonInstantiableMeta(type):
    def __call__(cls, *args, **kwargs):
        raise TypeError(f"{cls.__name__} class cannot be instantiated")

class NonInstantiable(metaclass=NonInstantiableMeta):
    pass