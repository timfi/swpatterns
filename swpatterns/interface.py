import inspect
from typing import Union, Type, Tuple, Callable, Dict, Any, List, Optional

__all__ = ("Interface", "implements", "isimplementation")


INTERFACE_LIST_NAME = "__interfaces__"
NONE_RELEVANT_VARS = ("__module__", "__doc__")


class InterfaceMeta(type):
    def __implementationcheck__(
        cls, impl: type, *, fuzzy: bool = False, skip_types: bool = False
    ) -> bool:
        """Return whether a type is a valid implementation of this interface.

        :param impl: the type to check
        :param skip_types: skip type checking, defaults to False
        :param fuzzy: check unregistered types as well, defaults to False
        """
        if hasattr(impl, INTERFACE_LIST_NAME):
            return cls in getattr(impl, INTERFACE_LIST_NAME)
        elif fuzzy:
            return _perform_check(impl, cls, skip_types, verbose=False)
        return False


class Interface(metaclass=InterfaceMeta):
    ...


def implements(
    interface: InterfaceMeta, *, skip_types: bool = False
) -> Callable[[type], type]:
    """Declare and validate an implementation of an interface.
    
    :param interface: the interface to declare/validate
    :param skip_types: skip type checking, defaults to False
    :raises TypeError: the implementation is not valid
    """

    def inner(cls: type) -> type:
        _perform_check(cls, interface, skip_types, verbose=True)
        original = getattr(cls, INTERFACE_LIST_NAME, tuple())
        setattr(
            cls,
            INTERFACE_LIST_NAME,
            ((interface,) + original if interface not in original else original),
        )
        return cls

    return inner


def isimplementation(
    impl: type, interface_or_tuple: Union[InterfaceMeta, Tuple[InterfaceMeta]]
) -> bool:
    """Return whether a type is a valid implementation of an interface.

    A tuple, as in isimplementation(x, (A, B, ...)), may be given as the target to check against.
    This is equivalent to isimplementation(x, A) or isimplementation(x, B) or ... etc.

    :param impl: the type to check
    :param interface_or_tuple: the target/s to check against
    :param skip_types: skip type checking, defaults to False
    :param fuzzy: check unregistered types as well, defaults to False
    :raises TypeError: the target is not or does not only contains sub-types of Interface
    """
    interfaces = (
        interface_or_tuple
        if isinstance(interface_or_tuple, tuple)
        else (interface_or_tuple,)
    )
    if not all(issubclass(interface, Interface) for interface in interfaces):
        raise TypeError(
            f"Can only check for implementation of interfaces: {interface_or_tuple}"
        )
    return any(
        getattr(interface, "__implementationcheck__")(impl) for interface in interfaces
    )


def _perform_check(
    impl: type, interface: InterfaceMeta, skip_types: bool, verbose: bool
) -> bool:
    """Execute all checks required by interface on a given implementation.
    
    :param impl: the implementation to check
    :param interface: interface to perform checks for
    :param skip_types: skip the checking of types/signatures
    :param verbose: throw verbose errors for decorator
    """
    checklist = {
        key: value
        for key, value in vars(interface).items()
        if key not in NONE_RELEVANT_VARS
    }
    targets = {
        key: value for key, value in vars(impl).items() if key not in NONE_RELEVANT_VARS
    }
    if not checklist:
        # No checks to perform?!
        return True
    for key, value in checklist.items():
        if key not in targets:
            if verbose:
                raise KeyError(f"{key} is not implement/defined")
            return False
        impl_value = targets[key]
        if not (skip_types or isinstance(impl_value, type(value))):
            if verbose:
                raise TypeError(f"{key}'s type doesn't match - should be {type(value)}")
            return False
        elif key == "__annotate__" and not skip_types:
            for attr_key, attr_type in value.items():
                try:
                    if attr_key in impl_value:
                        if impl_value[attr_key] is not attr_type:
                            raise TypeError
                    else:
                        impl_attr = getattr(impl, attr_key, None)
                        if impl_attr is not None and isinstance(impl_attr, attr_type):
                            raise TypeError
                except TypeError:
                    if verbose:
                        raise TypeError(
                            f"{attr_key}'s type doesn't match - should be {attr_type}"
                        )
                    return False
                if verbose:
                    raise KeyError(f"{attr_key} is not defined")
                return False
        elif callable(value):
            sig = inspect.signature(value)
            impl_sig = inspect.signature(impl_value)
            params = sig.parameters
            impl_params = impl_sig.parameters
            try:
                if len(params) != len(impl_params):
                    raise TypeError(
                        f"wrong amount of parameters - should be {impl_sig}"
                    )
                if not skip_types:
                    if (
                        sig.return_annotation is not sig.empty
                        and sig.return_annotation != impl_sig.return_annotation
                    ):
                        raise TypeError(
                            f"wrong return annotation - should be {sig.return_annotation}"
                        )
                for i, (param, impl_param) in enumerate(
                    zip(params.values(), impl_params.values())
                ):
                    if impl_param.kind is not param.kind:
                        raise TypeError(
                            f"parameter {i}({param.name}) has wrong kind - should be {param.kind}"
                        )
                    if (
                        not skip_types
                        and param.annotation is not param.empty
                        and impl_param.annotation is not param.annotation
                    ):
                        raise TypeError(
                            f"parameter {i}({param.name}) has wrong annotation - should be {param.annotation}"
                        )
            except TypeError as e:
                if verbose:
                    raise TypeError(f"{value}'s signature doesn't match: {e.args[0]}")
                return False
    return True
