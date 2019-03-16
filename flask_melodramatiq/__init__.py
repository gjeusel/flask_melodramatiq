import importlib
import functools
from flask_melodramatiq.lazy_broker import (
    broker_classes_registry,
    LazyActor,
    LazyBrokerMixin,
    Broker,
)

__all__ = ['LazyActor', 'Broker', 'RabbitmqBroker', 'RedisBroker', 'StubBroker']


def register_broker_class(module_name, class_name, default_url):
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        # We will raise this exact import error when the class is
        # instantiated by the user.
        raise_import_error = functools.partial(raise_error, e)
        broker_class = type(class_name, (), dict(
            __init__=raise_import_error,
            _LazyBrokerMixin__broker_factory=raise_import_error,
            _LazyBrokerMixin__broker_default_url=None,
        ))
    else:
        superclass = getattr(module, class_name)
        broker_class = type(class_name, (LazyBrokerMixin, superclass), dict(
            _LazyBrokerMixin__broker_factory=superclass,
            _LazyBrokerMixin__broker_default_url=default_url,
        ))
    broker_classes_registry[class_name] = broker_class
    return broker_class


def raise_error(e, *args, **kwargs):
    raise e


RabbitmqBroker = register_broker_class(
    module_name='dramatiq.brokers.rabbitmq',
    class_name='RabbitmqBroker',
    default_url='amqp://127.0.0.1:5672',
)


RedisBroker = register_broker_class(
    module_name='dramatiq.brokers.redis',
    class_name='RedisBroker',
    default_url='redis://127.0.0.1:6379/0',
)


StubBroker = register_broker_class(
    module_name='dramatiq.brokers.stub',
    class_name='StubBroker',
    default_url=None,
)
