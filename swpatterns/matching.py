from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Tuple, Union

__all__ = ("match", "_")


@dataclass
class MatchBranch:
    """A single branch of a match expression

    This encapsulates a single branch of a `match expression`, i.e a
    call to the match function. For easier usage it is aliased by `_`.
    """

    check: Any = None
    cond: Optional[Callable[[Any], bool]] = None
    func: Callable = field(init=False)

    def __rshift__(self, result: Any) -> MatchBranch:
        setattr(self, "func", result if callable(result) else (lambda: result))
        return self


_ = MatchBranch


def match(target: Any, *branches: MatchBranch) -> Any:
    """Match a target to patterns and evaluate expressions based on the first matching pattern.
    
    :param target: the target to perform branch checks on
    """
    for i, branch in enumerate(branches):
        check_result: Any = None
        if branch.cond is not None:
            if branch.cond(target):
                check_result = (target,)
        else:
            if branch.check == target:
                check_result = tuple()

        if i == len(branches) - 1 and branch.check is None:
            return branch.func()
        elif check_result is not None:
            return branch.func(*check_result)
    return None
