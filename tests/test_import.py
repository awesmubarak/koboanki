import importlib


def test_can_import() -> None:
    assert importlib.import_module("koboanki") is not None 