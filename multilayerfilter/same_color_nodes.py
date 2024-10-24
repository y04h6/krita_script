from krita import *
from collections import deque

#選択したピクセルの色を取得、同じ色を含むレイヤーを列挙して、マスク処理を施す
#レイヤーの透明度が一致しない場合は無視

def __getPixelColor(layer, x, y):
    """ 指定されたピクセルの色を取得（RGBA） """
    pixelData = layer.pixelData(x, y, 1, 1)
    b = pixelData[0]
    g = pixelData[1]
    r = pixelData[2]
    a = pixelData[3]
    return (r, g, b, a)

def __findDominantColorBfs(layer, maxSearch, width, height):
    """ 幅優先探索 """
    queue = deque()
    queue.append((0, 0, width, height))  # 最初に領域を追加
    i = 0
    while queue:
        x0, y0, x1, y1= queue.popleft()
        # 終了条件
        if x0+1 >= x1 or y0+1 >= y1 or i > maxSearch:
            continue

        # 中心のピクセルの色を取得
        x = (x0 + x1) // 2
        y = (y0 + y1) // 2
        r, g, b, a = __getPixelColor(layer, x, y)

        # 透明でない場合、その色を返す
        if int.from_bytes(a, 'little') > 0:
            print(f"x= {x} , y={y}, i={i}")
            return (int.from_bytes(r, 'little'), int.from_bytes(g, 'little'), int.from_bytes(b, 'little'))

        queue.append((x0, y0, x, y))  # 左上
        queue.append((x, y0, x1, y))  # 右上
        queue.append((x0, y, x, y1))  # 左下
        queue.append((x, y, x1, y1))  # 右下
        i+=1

    return None

def __findDominantColor(layer):
    app = Krita.instance()
    doc = app.activeDocument()

    # 代表的な色を取得
    if layer is not None and layer.type() == 'paintlayer':
        width = doc.width()
        height = doc.height()
        dominantColor = __findDominantColorBfs(layer, 4**8, width, height)
        
        if dominantColor is not None:
            print(f"代表的な色: RGB{dominantColor}")
        else:
            print("透明な領域しかありませんでした。")
    else:
        print("ペイントレイヤーが選択されていません。")
    return dominantColor

def __isSameColor(c1, c2):
    return c1[0] == c2[0] and c1[1] == c2[1] and c1[2] == c2[2]

def getSameColorNodeList():
    app = Krita.instance()
    doc = app.activeDocument()
    dominantColor = __findDominantColor(doc.activeNode())
    if dominantColor is None:
        return None
    # showNotification(f"色：{dominantColor}")
    sameColorNodes = []
    def func(nodes):
        for node in nodes:
            if node.type() == 'paintlayer':
                c=__findDominantColor(node)
                if c is not None and __isSameColor(c, dominantColor):
                    sameColorNodes.append(node)
            elif node.type() == 'grouplayer':
                func(node.childNodes())
    func(doc.topLevelNodes())
    return sameColorNodes



