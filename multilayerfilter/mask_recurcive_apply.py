from krita import *
from .log import *

def applyActiveMask():
    # Kritaインスタンスを取得
    app = Krita.instance()
    # アクティブなドキュメントを取得
    doc = app.activeDocument()
    if doc is None:
        printLog("ドキュメントが開かれていません。")
    else:
        printLog("ドキュメントが正常に取得されました。")

    applyMask(doc.activeNode())

def applyMask(maskNode):
    app = Krita.instance()
    doc = app.activeDocument()
    # アクティブなノードがフィルタマスクかどうか確認
    if maskNode is not None and maskNode.type().endswith('mask'):
        # フィルタマスクの親レイヤーを取得
        layer = maskNode.parentNode()

        if layer.type() == 'paintlayer':
            # レイヤーをフラット化（マスクを統合）
            doc.setActiveNode(layer)  # アクティブにする
            app.action('flatten_layer').trigger()  # マスクを統合
            printLog(f"{layer.name()} にフィルタマスクが適用され、レイヤーに統合されました。")
            
        elif layer.type() == 'grouplayer':
            def apply_mask_recursively(layers, mask):
                for layer in layers:
                    if not layer.visible():
                        continue
                    if layer.type() == 'paintlayer':
                        
                        # フィルタマスクをコピー
                        new_mask = mask.duplicate()
                        # ペイントレイヤーにマスクを適用
                        layer.addChildNode(new_mask, None)
                        printLog(f"フィルタマスクが {layer.name()} にコピーされました。")
                        
                        # レイヤーをフラット化（マスクを統合）
                        doc.setActiveNode(layer)  # アクティブにする
                        app.action('flatten_layer').trigger()  # マスクを統合
                        printLog(f"{layer.name()} にフィルタマスクが適用され、レイヤーに統合されました。")
                        
                    elif layer.type() == 'grouplayer':
                        # グループレイヤーの場合、その中のレイヤーに再帰的に適用
                        apply_mask_recursively(layer.childNodes(), mask)
            
            # フィルタマスクを兄弟レイヤーに再帰的に適用
            apply_mask_recursively(layer.childNodes(), maskNode)
            
            # 元のフィルタマスクを削除
            layer.removeChildNode(maskNode)
            printLog(f"{layer.name()} から元のフィルタマスクが削除されました。")
    else:
        printLog("選択されたノードはフィルタマスクではありません。")
