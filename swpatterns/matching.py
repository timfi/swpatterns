from __future__ import annotations
from dataclasses import dataclass, field
import sys
from typing import (
    Any,
    Callable,
    Optional,
    Tuple,
    Union,
    Dict,
    ClassVar,
    Generic,
    TypeVar,
    Type,
    List,
)

from .composition import Compose
from .interface import Interface, implements, isimplementation

__all__ = ("match", "_")


def match(target: Any, *branches: MatchBranch) -> Any:
    """Match a target to patterns and evaluate expressions based on the first matching pattern.
    
    :param target: the target to perform branch checks on
    :param branches: the branches to check
    """
    if not all(isimplementation(branch, _IMatchBranch) for branch in branches):
        raise TypeError("Custom branches must implement `_IMatchBranch` interface.")
    for i, branch in enumerate(branches):
        check_result = branch.check(target)
        if check_result is not None:
            return branch.apply(check_result)
    return None


@dataclass
class _MatchBranchData:
    """MatchBranch data holder."""

    check_val: Any = field(init=False, default=None)
    func: Callable = field(init=False, default=lambda: None)


class _IMatchBranch(Interface):
    """MatchBranch interface."""

    def check(self, target: Any) -> Optional[Tuple]:
        ...


@implements(_IMatchBranch)
class MatchBranch(
    Compose(_MatchBranchData, "check_val", name="_mb")  # type: ignore
):
    """Match branch with no checks."""

    def __init_subclass__(cls, symbol: Optional[str] = None) -> None:
        if symbol is not None:
            setattr(MatchBranch, symbol, cls)

    def __init__(self, check_val: Any = None):
        super().__init__()
        self.check_val = check_val

    def __rshift__(self, result: Any) -> MatchBranch:
        setattr(self._mb, "func", result if callable(result) else (lambda: result))
        return self

    def check(self, target: Any) -> Optional[Tuple]:
        return tuple()

    def apply(self, args: Tuple) -> Any:
        return self._mb.func(*args)


_ = MatchBranch


@implements(_IMatchBranch)
class Literal(MatchBranch, symbol="l"):
    """Matching branch with a literal compare value."""

    check_val: Any

    def check(self, target: Any) -> Optional[Tuple]:
        if self.check_val == target:
            return tuple()
        return None


@implements(_IMatchBranch)
class Conditional(MatchBranch, symbol="c"):
    """Matching branch with a conditional."""

    check_val: Callable

    def check(self, target: Any) -> Optional[Tuple]:
        if self.check_val(target):
            return (target,)
        return None


@implements(_IMatchBranch)
class Struct(MatchBranch, symbol="s"):
    """Matching branch with 'struct' decomposition."""

    _type: type
    check_val: Tuple[Tuple, Dict]

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.check_val = (args, kwargs)

    def __class_getitem__(cls, type_: type) -> Type[Struct]:
        return type(f"{type_.__name__}MatchBrach", (Struct,), {"_type": type_})

    def check(self, target: Any) -> Optional[Tuple]:
        if isinstance(target, self._type):
            args, kwargs = self.check_val
            try:
                if all(
                    getattr(target, attr) == val
                    if not callable(val)
                    else val(getattr(target, attr))
                    for attr, val in kwargs.items()
                ):
                    return tuple(getattr(target, attr) for attr in args)
            except AttributeError:
                ...
        return None
