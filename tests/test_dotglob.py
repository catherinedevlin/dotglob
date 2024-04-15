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


def test_expressions_no_globfiles(dirtree):
    expressions_found = list(globber.expressions(dirtree, cfg=globber.Config()))
    assert len(expressions_found) == 0


def test_expressions_single_globfile(dirtree):
    cfg = globber.Config()
    (dirtree / cfg.globfile).write_text(
        """
        *.py
        *.txt """
    )
    expressions_found = list(globber.expressions(dirtree, cfg=cfg))
    assert len(expressions_found) == 2
    assert expressions_found[0].endswith("dir1/*.py")
    assert expressions_found[1].endswith("dir1/*.txt")


def test_expressions_multi_globfiles(dirtree):
    cfg = globber.Config()
    (dirtree / cfg.globfile).write_text(
        """
        *.py
        *.txt """
    )
    (dirtree / "dir2" / cfg.globfile).write_text("-*.py")
    expressions_found = list(globber.expressions(dirtree, cfg=cfg))
    assert len(expressions_found) == 3


def test_expressions_sorted_by_depth(dirtree):
    cfg = globber.Config()
    (dirtree / "dir2" / "dir3" / cfg.globfile).write_text("-**.txt")
    (dirtree / "dir2" / cfg.globfile).write_text("-*.py")
    (dirtree / cfg.globfile).write_text(
        """
        *.py
        *.txt """
    )
    expressions_found = list(globber.expressions(dirtree, cfg=cfg))
    assert "dir3" in expressions_found[3]
    assert "dir3" not in expressions_found[2]
    assert "dir2" in expressions_found[2]


def test_expressions_relativized(dirtree):
    cfg = globber.Config()
    (dirtree / cfg.globfile).write_text(
        """
        **.py
        *.txt """
    )
    (dirtree / "dir2" / cfg.globfile).write_text("-*.md")
    expressions_found = list(globber.expressions(dirtree, cfg=cfg))
    assert len(expressions_found) == 3
    assert expressions_found[0].endswith("dir1/**.py")
    assert expressions_found[1].endswith("dir1/*.txt")
    assert expressions_found[2].startswith("-")
    assert expressions_found[2].endswith("dir1/dir2/*.md")


def test_glob_all(dirtree):
    cfg = globber.Config()
    (dirtree / cfg.globfile).write_text("**")
    expressions_found = list(globber.expressions(dirtree, cfg=cfg))
    paths = globber.paths(expressions_found)
    assert len(paths) == 13


def test_glob_all_implied(dirtree):
    cfg = globber.Config()
    (dirtree / cfg.globfile).touch()
    expressions_found = list(globber.expressions(dirtree, cfg=cfg))
    paths = globber.paths(expressions_found)
    assert len(paths) == 13


def test_omit_dir2(dirtree):
    cfg = globber.Config()
    (dirtree / cfg.globfile).write_text("** -dir2/**")
    expressions_found = list(globber.expressions(dirtree, cfg=cfg))
    paths = globber.paths(expressions_found)
    assert len(paths) == 6
    for path in paths:
        assert "dir2/" not in path


def test_omit_dir2_abbrev(dirtree):
    cfg = globber.Config()
    (dirtree / cfg.globfile).touch()
    (dirtree / "dir2" / cfg.globfile).write_text("-.py")
    expressions_found = list(globber.expressions(dirtree, cfg=cfg))
    paths = globber.paths(expressions_found)
    for path in paths:
        assert "dir2/mod1.py" not in path


def test_omit_extension(dirtree):
    cfg = globber.Config()
    (dirtree / cfg.globfile).touch()
    (dirtree / "dir2" / cfg.globfile).write_text("-.py")
    expressions_found = list(globber.expressions(dirtree, cfg=cfg))
    paths = globber.paths(expressions_found)
    for path in paths:
        if "dir2" in path:
            assert ".py" not in path


def test_unabbreviate_unaltered():
    assert globber.unabbreviated("**/*.py") == "**/*.py"


def test_unabbreviate_negative_unaltered():
    assert globber.unabbreviated("-**/*.py") == "-**/*.py"


def test_unabbreviate_ext():
    assert globber.unabbreviated(".py") == "**/*.py"


def test_unabbreviate_negative_ext():
    assert globber.unabbreviated("-.py") == "-**/*.py"


def test_unabbreviate_negative_empty():
    assert globber.unabbreviated("-") == "-**"
