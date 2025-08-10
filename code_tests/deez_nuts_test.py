class BaseDeezNuts:
    def deez_nuts(self):
        print("foo()")


class RaiseDeezNuts(BaseDeezNuts):
    def deez_nuts(self):
        print("ahhhhh()")


class AnotherDeezNuts(BaseDeezNuts):
    def deez_nuts(self):
        print("oh noooo()")


def call_all_deez_nuts():
    for subclass in BaseDeezNuts.__subclasses__():
        instance = subclass()
        print(f"Calling {subclass.__name__}...")
        instance.deez_nuts()


call_all_deez_nuts()
