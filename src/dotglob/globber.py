import glob
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class Config:
    globfile = ".glob"
    absolute_path = False


def to_additive(expression: str) -> tuple[str, bool]:
    """
    >>> to_additive('blah.txt')
    ('blah.txt', True)
    >>> to_additive('-blah.txt')
    ('blah.txt', False)
    """
    if expression.startswith("-"):
        return (expression.lstrip("-").strip(), False)
    return (expression, True)


def unabbreviated(expression: str) -> str:
    (expression, additive) = to_additive(expression)
    sign = "" if additive else "-"
    expression = expression or "**"
    if expression.startswith("."):
        expression = f"**/*{expression}"
    return f"{sign}{expression}"


def unordered_expressions(path: Path, cfg: Config) -> Iterable[str]:
    for globfile in path.glob(f"**/{cfg.globfile}"):
        for expression in shlex.split(globfile.read_text() or "**"):
            expression = unabbreviated(expression)
            if expression.startswith("-"):
                yield f"-{globfile.parent / expression[1:]}"
            else:
                yield f"{globfile.parent / expression}"


def expressions(path: Path, cfg: Config) -> list[str]:
    """All glob expressions found in globfiles under dir

    Results are ordered in level of increasing directory
    depth, so that they can be applied in that order, and
    deeper (more specific) results will overwrite shallower

    Args:
        path (Path): Root of directory tree to search
        cfg (Config): Global configuration

    Returns:
        list[str]: glob expressions, possibly prefixed with '-'
    """

    result = list(unordered_expressions(path, cfg))
    result.sort(key=lambda x: x.count("/"))  # Backslash on Windows?
    return result


def paths(expressions: Iterable[str]) -> set[Path]:
    result = set()
    for expr in expressions:
        (expression, additive) = to_additive(expr)
        glob_results = set(glob.glob(expression, recursive=True, include_hidden=True))
        if additive:
            result |= glob_results
        else:
            result -= glob_results
    return result
