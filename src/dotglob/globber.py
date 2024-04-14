import shlex
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    globfile = ".glob"
    absolute_path = False


def expressions(path: Path, cfg: Config):
    for globfile in path.glob(f"**/{cfg.globfile}"):
        for expression in shlex.split(globfile.read_text()):
            if expression.startswith('-'):
                yield f"-{globfile.parent / expression[1:]}"
            else:
                yield f"{globfile.parent / expression}"



