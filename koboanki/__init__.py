from __future__ import annotations

"""Package root – re-export core helpers and (when inside Anki) register UI."""

from importlib import import_module
from importlib.util import find_spec

from .core import *  # re-export helper API  noqa: F403,F401

# Only register the GUI integration when running *inside* Anki – i.e. both the
# `aqt` package can be imported **and** it already exposed a `mw` (main
# window) object.  This guards against accidental Qt imports during unit
# tests.

if find_spec("aqt") is not None:  # pragma: no cover
    aqt = import_module("aqt")

    if getattr(aqt, "mw", None) is not None:
        from .anki_plugin import setup as _setup  # noqa: F401 – side-effect

        _setup() 