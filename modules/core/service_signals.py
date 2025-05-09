from django.dispatch import Signal

# Dictionary to store signals globally if needed
REGISTERED_SIGNALS = {}

def register_signal(signal_name):
    """
    Decorator factory to register a function as a receiver for a custom signal.

    Args:
        signal_name (str): A unique name to register the signal.

    Returns:
        function: The decorated function, connected to the signal.
    """
    signal = REGISTERED_SIGNALS.get(signal_name)
    if not signal:
        signal = Signal()
        REGISTERED_SIGNALS[signal_name] = signal

    def decorator(func):
        signal.connect(func)
        func._signal = signal  # Optional: store reference for introspection
        return func

    return decorator
