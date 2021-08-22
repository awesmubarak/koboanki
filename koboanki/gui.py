from aqt import mw
from aqt.utils import showInfo
from aqt.qt import QDialog

class PluginWindow(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
