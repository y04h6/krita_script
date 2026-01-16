from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from krita import *
from .same_color_nodes import *
from .mask_recurcive_apply import *
import time

RESOLUSION=100

def showNotification(message):
    """通知ダイアログを表示"""
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setText(message)
    msg_box.setWindowTitle("通知")
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()

class MaskData:
    def __init__(self, layer):
        app = Krita.instance()
        doc = app.activeDocument()
        self.name = layer.name()
        self.filter = app.filter("hsvadjustment")
        self.configParameters=InfoObject()
        self.configParameters.setProperties({
                'colorize': False,
                'compatibilityMode': False,
                'type': 1,
                'h': 0,
                's': 0,
                'v': 0
            })
        self.filter.setConfiguration(self.configParameters)
        self.targetLayer=layer
        selection=Selection()
        selection.select(0,0,doc.width(), doc.height(), 255)
        self.filterMask = doc.createFilterMask("HSV Adjustment", self.filter, selection)
        printLog(f"{layer.name()} にフィルタマスクを作成しました。")
        self.targetLayer.addChildNode(self.filterMask, None)

    def merge(self):
        #mergeLayer(self.targetLayer)
        applyMask(self.filterMask)
        #self.targetLayer = self.doc.activeNode()

    def resetName(self):
        self.targetLayer.setName(self.name)

    def remove(self):
        self.targetLayer.removeChildNode(self.filterMask)


class HSVAdjustmentDialog(QDialog):
    def __init__(self, targetNodes):
        super().__init__()
        self.app = Krita.instance()
        self.doc = self.app.activeDocument()

        self.setWindowTitle("HSV Adjustment")
        self.setGeometry(300, 300, 400, 200)

        # スライダーとラベルを作成
        self.hueLabel = QLabel('H:', self)
        self.hueSlider = QSlider(Qt.Horizontal, self)
        self.hueSlider.setMinimum(-180*RESOLUSION)
        self.hueSlider.setMaximum(180*RESOLUSION)
        self.hueSlider.setValue(0)

        self.saturationLabel = QLabel('S:', self)
        self.saturationSlider = QSlider(Qt.Horizontal, self)
        self.saturationSlider.setMinimum(-100*RESOLUSION)
        self.saturationSlider.setMaximum(100*RESOLUSION)
        self.saturationSlider.setValue(0)

        self.valueLabel = QLabel('V:', self)
        self.valueSlider = QSlider(Qt.Horizontal, self)
        self.valueSlider.setMinimum(-100*RESOLUSION)
        self.valueSlider.setMaximum(100*RESOLUSION)
        self.valueSlider.setValue(0)

        self.checkboxColorize = QCheckBox("Colorize", self)

        # 更新を遅延させるためのタイマー
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_hsv)

        # ボタンを作成
        self.resetButton = QPushButton('Reset', self)
        self.applyButton = QPushButton('Apply', self)

        # レイアウトを作成
        layout = QVBoxLayout()

        sublayout = QHBoxLayout()
        sublayout.addWidget(self.hueLabel)
        sublayout.addWidget(self.hueSlider)
        layout.addLayout(sublayout)

        sublayout = QHBoxLayout()
        sublayout.addWidget(self.saturationLabel)
        sublayout.addWidget(self.saturationSlider)
        layout.addLayout(sublayout)
        
        sublayout = QHBoxLayout()
        sublayout.addWidget(self.valueLabel)
        sublayout.addWidget(self.valueSlider)
        layout.addLayout(sublayout)
        
        sublayout = QHBoxLayout()
        sublayout.addWidget(self.checkboxColorize)
        sublayout.addWidget(self.resetButton)
        sublayout.addWidget(self.applyButton)
        layout.addLayout(sublayout)
        
        self.setLayout(layout)

        # スライダーの値が変更されたときのイベント
        self.hueSlider.valueChanged.connect(self.schedule_update)
        self.saturationSlider.valueChanged.connect(self.schedule_update)
        self.valueSlider.valueChanged.connect(self.schedule_update)
        self.resetButton.clicked.connect(self.resetParam)
        self.applyButton.clicked.connect(self.apply_adjustment)
        self.checkboxColorize.stateChanged.connect(self.schedule_update)
        self.closeEvent = self.cancel

        # フィルターマスク作成
        self.maskList=[]
        nodeSet=set()
        
        for node in targetNodes:
            nodeSet.add(node.uniqueId())

        for node in targetNodes:
            # 親子関係のノードがある場合、二重でマスクしないように子は選択から外す
            if self.checkParent(node.parentNode(), nodeSet):
                self.maskList.append(MaskData(node))
                printLog('target:'+node.name())
    
    def checkParent(self, node, nodeSet):
        if node == None:
            return True
        if node.uniqueId() in nodeSet:
            return False
        return self.checkParent(node.parentNode(), nodeSet)

    def resetParam(self):
        self.hueSlider.setValue(0)
        self.saturationSlider.setValue(0)
        self.valueSlider.setValue(0)
        self.checkboxColorize.setCheckState(Qt.Unchecked)

    def schedule_update(self):
        """スライダー操作時に遅延して更新をスケジュール"""
        self.update_timer.start(200)  # 200ms待機してから更新

    def update_hsv(self):
        # スライダーの現在値を取得
        hue_shift = self.hueSlider.value()
        saturation_scale = self.saturationSlider.value()
        value_scale = self.valueSlider.value()
        colorize = self.checkboxColorize.isChecked()

        # # フィルタのパラメータを設定
        for mask in self.maskList:
            mask.configParameters.setProperties({
                    'colorize': colorize,
                    'compatibilityMode': False,
                    'type': 1,
                    'h': (hue_shift/RESOLUSION+360)%360,
                    's': saturation_scale/RESOLUSION,
                    'v': value_scale/RESOLUSION
                })
            mask.filterMask.setFilter(mask.filter)
        # ドキュメントを更新
        self.doc.refreshProjection()

    def apply_adjustment(self):
        self.update_hsv()
        for mask in self.maskList:
            mask.merge()
        # ドキュメントを更新
        self.doc.waitForDone()
        self.doc.refreshProjection()
        # FIXME:レイヤー名を元に戻す（うまく動作しない。おそらくタイミングが悪い）
        for mask in self.maskList:
            mask.resetName()
        # showNotification(logString)
        self.close()
    
    def cancel(self, event):
        # 適用しない場合は、作ったマスクレイヤーを削除する
        for mask in self.maskList:
            mask.remove()
        self.doc.waitForDone()
        self.doc.refreshProjection()

def hsvAdjustForSelectNodes():
    # Kritaのアプリケーションからウィンドウを表示
    window = Krita.instance().activeWindow()
    view = window.activeView()
    nodes=view.selectedNodes()
    window = HSVAdjustmentDialog(nodes)
    window.exec_()

def hsvAdjustForSameColorNodes():
    # Kritaのアプリケーションからウィンドウを表示
    window = Krita.instance().activeWindow()
    nodes=getSameColorNodeList()
    if nodes is None:
        showNotification("現在のレイヤーの主要な色を取得できませんでした")
        return
    window = HSVAdjustmentDialog(nodes)
    window.exec_()

# Kritaのスクリプトから実行
# runExtension()
