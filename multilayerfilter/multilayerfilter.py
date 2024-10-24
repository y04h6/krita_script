# BBD's Krita Script Starter Feb 2018

from krita import Extension
from .hsv_adjustment import *

class Multilayerfilter(Extension):

    def __init__(self, parent):
        # Always initialise the superclass.
        # This is necessary to create the underlying C++ object
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction('pykrita_multilayerfilterSelect', i18n('選択レイヤーHSV調整'), "tools/scripts")
        action.triggered.connect(hsvAdjustForSelectNodes)
        action = window.createAction('pykrita_multilayerfilterSameColor', i18n('同色レイヤーHSV調整'), "tools/scripts")
        action.triggered.connect(hsvAdjustForSameColorNodes)

