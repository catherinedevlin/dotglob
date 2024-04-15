import glob
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class Config:
    globfile = ".glob"
    absolute_path = False


def unordered_expressions(path: Path, cfg: Config) -> Iterable[str]:
    for globfile in path.glob(f"**/{cfg.globfile}"):
        for expression in shlex.split(globfile.read_text()):
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
    for expression in expressions:
        if expression.startswith("-"):
            result -= set(
                glob.glob(expression[1:], recursive=True, include_hidden=True)
            )
        else:
            result |= set(glob.glob(expression, recursive=True, include_hidden=True))
    return result


# Implied ** on bare .extension specs?
# Possibly a configuration
# What about empty .glob file?
# Note that including dir2/** does not include dir2,
# and excluding dir2/** does not exclude dir2
