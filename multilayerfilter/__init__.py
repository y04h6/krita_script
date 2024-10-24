from krita import *
from .multilayerfilter import Multilayerfilter

# And add the extension to Krita's list of extensions:
app = Krita.instance()
# Instantiate your class:
extension = Multilayerfilter(parent = app)
app.addExtension(extension)
