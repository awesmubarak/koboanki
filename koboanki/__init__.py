"""Koboanki v3

Minimal entry-point that registers a toolbar button in Anki which, when clicked,
shows a simple "hi" message box.  This is used as a quick sanity check that the
add-on loads correctly in current Anki builds.

When this package is imported *outside* of Anki (for example while running unit
or type-checking tests) we fall back to light-weight stubs so that the import
succeeds even though the real ``aqt``/``anki`` modules are missing.
"""
from __future__ import annotations

import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional runtime imports – only available when the code is executed inside
# a running Anki/Qt context.  Outside that environment we expose minimal stubs
# so that *import koboanki* still works.
# ---------------------------------------------------------------------------
try:
    from aqt import gui_hooks  # type: ignore
    from aqt.qt import QAction, QMessageBox  # type: ignore
    from aqt.utils import qconnect  # type: ignore
except ImportError:  # pragma: no cover – executed in CI / dev env

    class _Stub:  # pylint: disable=too-few-public-methods
        """Very small stand-in object so attribute access doesn't crash."""

        def __getattr__(self, name: str) -> "_Stub":  # noqa: D401
            return self

        def __call__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401
            return None

    gui_hooks = _Stub()  # type: ignore
    QAction = _Stub  # type: ignore
    QMessageBox = _Stub  # type: ignore

    def qconnect(signal: Any, slot: Callable[..., Any]) -> None:  # type: ignore
        """Stub replacement for aqt.utils.qconnect."""
        return None

    logger.debug("Running outside Anki – GUI functionality stubbed.")
else:

    def _show_hi() -> None:  # noqa: D401
        """Display a friendly greeting."""

        QMessageBox.information(None, "Koboanki", "hi")  # type: ignore[attr-defined]

    def _add_toolbar_button(main_window):  # type: ignore  # noqa: D401, ANN001
        """Insert the button into Anki's main toolbar once it is initialised."""

        action = QAction("Koboanki", main_window)
        qconnect(action.triggered, _show_hi)  # type: ignore[arg-type]

        # Insert directly before the *Browse* button for visibility.
        try:
            browse_action = main_window.form.actionBrowse  # type: ignore[attr-defined]
            main_window.form.toolbar.insertAction(browse_action, action)  # type: ignore[arg-type]
        except Exception as exc:  # pragma: no cover
            logger.warning("Unable to insert toolbar action before Browse: %s", exc)
            main_window.form.toolbar.addAction(action)

    # Register with Anki's hook system so we run at the right time.
    gui_hooks.main_window_did_init.append(_add_toolbar_button)


__all__ = [
    "logger",
] 