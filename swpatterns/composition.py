from operator import attrgetter
from typing import Union, Tuple, Any, Dict

from .interface import InterfaceMeta, isimplementation

__all__ = ("Compose",)


def Compose(
    type_: type,
    *fields: Union[str, Tuple[str, str]],
    name: str = None,
    build: bool = True,
    args: Tuple = tuple(),
    kwargs: Dict[str, Any] = dict(),
) -> type:
    """Generate a new type that encompasses the forwarding of the given fields
    
    :param type_: the type to composee
    :param *fields: the fields to forward
    :param name: the name to give the composee, defaults to f"_{type_.__name__.lower()}"
    :param build: enable the automatic generation of a composee instance, doesn nothing when an interface is supplied
    :param args: the positional arguments to call the constructor of type_ with, defaults to tuple()
    :param kwargs: the keyword arguments to call the constructor of type_ with, defaults to dict()
    :return: the inheritable type
    """
    name_ = name or f"_{type_.__name__.lower()}"
    fields_ = [
        (field, field) if not isinstance(field, tuple) else field for field in fields
    ]

    class InheritableComposition:
        def __init_subclass__(cls):
            super().__init_subclass__()
            for origin, dest in fields_:
                setattr(cls, dest, _build_field(name_, origin))

        def __init__(self, *args_, **kwargs_):
            obj = kwargs_.pop(name_, None)
            if not obj:
                if build and not isinstance(type_, InterfaceMeta):
                    obj = type_(*args, **kwargs)
                else:
                    raise ValueError(
                        f"Need to provide a instance of type {type_} under kwarg {name_}."
                    )
            elif isinstance(type_, InterfaceMeta) and not isimplementation(
                type(obj), type_
            ):
                raise TypeError(f"Passed instance doesn't implement {type_}")
            if any(not hasattr(obj, attr) for attr, _ in fields_):
                raise TypeError(
                    "Can't initialise class due to missing fields required by composition "
                    f"(composite: {self.__class__}, composee: {type_}).\n"
                    f"Missing fields: {[attr for attr, _ in fields_ if not hasattr(obj, attr)]}"
                )
            setattr(self, name_, obj)
            super().__init__(*args_, **kwargs_)

    return InheritableComposition


def _build_field(name: str, field: str) -> property:
    """Build a single forwarding property to encompass the requested field
    
    :param name: the name given to the composee
    :param field: the field to forward
    :return: the generated property
    """
    obj_getter = attrgetter(name)

    def getter(self):
        return getattr(obj_getter(self), field)

    def setter(self, value):
        return setattr(obj_getter(self), field, value)

    def deleter(self):
        return delattr(obj_getter(self), field)

    return property(getter, setter, deleter)
