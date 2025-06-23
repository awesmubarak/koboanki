import importlib


def test_can_import():
    assert importlib.import_module("koboanki") is not None 