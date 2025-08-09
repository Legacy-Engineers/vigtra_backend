import logging
import inspect
from typing import Dict, Callable, Any, Optional
from functools import wraps
from django.dispatch import Signal
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

# Dictionary to store signals globally
REGISTERED_SIGNALS: Dict[str, Signal] = {}


class SignalRegistry:
    """
    A registry class to manage custom Django signals with better organization
    and additional features like signal discovery and cleanup.
    """

    def __init__(self):
        self._signals: Dict[str, Signal] = {}
        self._receivers: Dict[str, list] = {}

    def get_or_create_signal(
        self, signal_name: str, providing_args: Optional[list] = None
    ) -> Signal:
        """
        Get an existing signal or create a new one.

        Args:
            signal_name: Unique name for the signal
            providing_args: List of argument names the signal will provide (deprecated in Django 4.0+)

        Returns:
            Signal instance
        """
        if signal_name not in self._signals:
            # Django 4.0+ doesn't use providing_args, but we maintain backward compatibility
            try:
                self._signals[signal_name] = Signal(providing_args=providing_args)
            except TypeError:
                # Django 4.0+ - providing_args is no longer supported
                self._signals[signal_name] = Signal()

            self._receivers[signal_name] = []
            logger.info(f"Created new signal: {signal_name}")

        return self._signals[signal_name]

    def get_signal(self, signal_name: str) -> Optional[Signal]:
        """Get a signal by name without creating it."""
        return self._signals.get(signal_name)

    def list_signals(self) -> Dict[str, int]:
        """List all registered signals and their receiver counts."""
        return {
            name: len(self._receivers.get(name, [])) for name in self._signals.keys()
        }

    def disconnect_all(self, signal_name: str) -> int:
        """Disconnect all receivers from a signal."""
        if signal_name not in self._signals:
            return 0

        signal = self._signals[signal_name]
        receivers = self._receivers.get(signal_name, [])

        for receiver in receivers:
            signal.disconnect(receiver)

        count = len(receivers)
        self._receivers[signal_name] = []
        logger.info(f"Disconnected {count} receivers from signal: {signal_name}")
        return count

    def register_receiver(self, signal_name: str, receiver: Callable):
        """Register a receiver function for a signal."""
        if signal_name not in self._receivers:
            self._receivers[signal_name] = []
        self._receivers[signal_name].append(receiver)


# Global registry instance
signal_registry = SignalRegistry()


def register_signal(
    signal_name: str,
    providing_args: Optional[list] = None,
    sender: Optional[Any] = None,
    weak: bool = True,
    dispatch_uid: Optional[str] = None,
    auto_load: bool = True,
) -> Callable:
    """
    Enhanced decorator factory to register a function as a receiver for a custom signal.

    Args:
        signal_name: A unique name to register the signal
        providing_args: List of argument names the signal will provide (deprecated in Django 4.0+)
        sender: Only receive signals sent by particular sender
        weak: Whether to use weak references for the receiver
        dispatch_uid: Unique identifier for the receiver
        auto_load: Whether to automatically connect the receiver (default: True)

    Returns:
        Decorated function connected to the signal

    Raises:
        ValueError: If signal_name is empty or None
        ImproperlyConfigured: If Django apps are not ready
    """
    if not signal_name or not isinstance(signal_name, str):
        raise ValueError("signal_name must be a non-empty string")

    # Check if Django apps are ready (for production safety)
    if auto_load:
        try:
            apps.check_apps_ready()
        except ImproperlyConfigured as e:
            logger.warning(
                f"Django apps not ready when registering signal '{signal_name}': {e}"
            )

    def decorator(func: Callable) -> Callable:
        if not callable(func):
            raise TypeError("Decorated object must be callable")

        # Get or create the signal
        signal = signal_registry.get_or_create_signal(signal_name, providing_args)

        # Create a wrapper to preserve function metadata and add error handling
        # Django signal receivers must accept **kwargs
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Only pass the original function's expected arguments
                # Django signals will pass additional kwargs that the original function might not expect
                sig = inspect.signature(func)
                # Filter kwargs to only include parameters that the original function accepts
                filtered_kwargs = {}
                for param_name, param in sig.parameters.items():
                    if param_name in kwargs:
                        filtered_kwargs[param_name] = kwargs[param_name]

                return func(*args, **filtered_kwargs)
            except Exception as e:
                logger.error(
                    f"Error in signal receiver '{func.__name__}' for signal '{signal_name}': {e}"
                )
                raise

        # Connect the signal if auto_load is True
        if auto_load:
            signal.connect(
                wrapper,
                sender=sender,
                weak=weak,
                dispatch_uid=dispatch_uid or f"{signal_name}_{func.__name__}",
            )
            signal_registry.register_receiver(signal_name, wrapper)
            logger.debug(
                f"Connected receiver '{func.__name__}' to signal '{signal_name}'"
            )

        # Add metadata to the function for introspection
        wrapper._signal = signal
        wrapper._signal_name = signal_name
        wrapper._signal_metadata = {
            "providing_args": providing_args,
            "sender": sender,
            "weak": weak,
            "dispatch_uid": dispatch_uid,
            "auto_load": auto_load,
        }

        # Add utility methods
        def manual_connect():
            """Manually connect this receiver to its signal."""
            signal.connect(
                wrapper,
                sender=sender,
                weak=weak,
                dispatch_uid=dispatch_uid or f"{signal_name}_{func.__name__}",
            )
            signal_registry.register_receiver(signal_name, wrapper)

        def disconnect():
            """Disconnect this receiver from its signal."""
            signal.disconnect(
                wrapper,
                sender=sender,
                dispatch_uid=dispatch_uid or f"{signal_name}_{func.__name__}",
            )

        wrapper.manual_connect = manual_connect
        wrapper.disconnect = disconnect

        return wrapper

    return decorator


def send_signal(signal_name: str, sender: Any = None, **kwargs) -> list:
    """
    Send a custom signal by name.

    Args:
        signal_name: Name of the signal to send
        sender: The sender of the signal
        **kwargs: Additional arguments to pass to receivers

    Returns:
        List of (receiver, response) tuples

    Raises:
        ValueError: If signal doesn't exist
    """
    signal = signal_registry.get_signal(signal_name)
    if not signal:
        raise ValueError(f"Signal '{signal_name}' is not registered")

    logger.debug(f"Sending signal '{signal_name}' from sender: {sender}")
    return signal.send(sender=sender, **kwargs)


def get_signal_info(signal_name: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a registered signal.

    Args:
        signal_name: Name of the signal

    Returns:
        Dictionary with signal information or None if not found
    """
    signal = signal_registry.get_signal(signal_name)
    if not signal:
        return None

    return {
        "name": signal_name,
        "signal": signal,
        "receiver_count": len(signal_registry._receivers.get(signal_name, [])),
        "receivers": signal_registry._receivers.get(signal_name, []),
    }


# Backward compatibility
REGISTERED_SIGNALS = signal_registry._signals

# Usage examples:
"""
# Basic usage
@register_signal('user_registered')
def handle_user_registration(sender, user, **kwargs):
    print(f"User {user.username} registered!")

# Advanced usage with options
@register_signal(
    'payment_processed',
    providing_args=['amount', 'currency'],
    sender='PaymentProcessor',
    dispatch_uid='payment_logger'
)
def log_payment(sender, amount, currency, **kwargs):
    print(f"Payment of {amount} {currency} processed")

# Manual connection (auto_load=False)
@register_signal('delayed_task', auto_load=False)
def handle_delayed_task(sender, **kwargs):
    print("Handling delayed task")

# Connect manually later
handle_delayed_task.manual_connect()

# Send signals
send_signal('user_registered', sender=None, user=some_user)
send_signal('payment_processed', sender='PaymentProcessor', amount=100, currency='USD')

# Get signal information
info = get_signal_info('user_registered')
print(f"Signal has {info['receiver_count']} receivers")

# List all signals
print(signal_registry.list_signals())
"""
