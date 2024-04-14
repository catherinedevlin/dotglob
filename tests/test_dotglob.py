import pytest

from dotglob import globber


@pytest.fixture
def dirtree(tmp_path):
    dir1 = tmp_path / "dir1"
    dir1.mkdir()
    (dir1 / "README.md").touch()
    (dir1 / "script1.py").touch()
    (dir1 / "script2.py").touch()
    dir2 = dir1 / "dir2"
    dir2.mkdir()
    (dir2 / "doc1.md").touch()
    (dir2 / "mod1.py").touch()
    (dir2 / "doc2.pdf").touch()
    dir3 = dir2 / "dir3"
    dir3.mkdir()
    (dir3 / "doc3.txt").touch()
    (dir3 / "doc4.txt").touch()
    (dir3 / "darn-notepad.md.txt").touch()
    dir4 = tmp_path / "dir4"
    dir4.mkdir()
    (dir4 / "doc5.md").touch()
    (dir4 / "doc6.odf").touch()
    baddir = tmp_path / "ugly, dumb - bad dir name"
    baddir.mkdir()
    (baddir / "script3.py").touch()
    (baddir / "doc7.md").touch()
    return dir1


def test_patterns_no_globfiles(dirtree):
    patterns_found = list(globber.patterns(dirtree, cfg=globber.Config()))
    assert len(patterns_found) == 0


def test_patterns_single_globfile(dirtree):
    cfg = globber.Config()
    (dirtree / cfg.globfile).write_text(
        """
        *.py
        *.txt """
    )
    patterns_found = list(globber.patterns(dirtree, cfg=cfg))
    assert patterns_found == ["*.py", "*.txt"]


def test_patterns_multi_globfiles(dirtree):
    cfg = globber.Config()
    (dirtree / cfg.globfile).write_text(
        """
        *.py
        *.txt """
    )
    (dirtree / "dir2" / cfg.globfile).write_text("-*.py")
    patterns_found = list(globber.patterns(dirtree, cfg=cfg))
    assert len(patterns_found) == 3
