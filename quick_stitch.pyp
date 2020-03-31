
import os
import sys
import c4d

PLUGIN_ID = 1054816

class QuickStitch(c4d.plugins.ObjectData):
    def __init__(self, *args):
        self.SetOptimizeCache(True)

    def Init(self, op):
        self.InitAttr(op, float, c4d.QUICK_STITCH_COUNT)
        self.InitAttr(op, float, c4d.QUICK_STITCH_STEP)

        op[c4d.QUICK_STITCH_COUNT] = 50

        return True



if __name__ == "__main__":
    # Retrieves the icon path
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "opyspherifymodifier.tif")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    # Registers the object plugin
    c4d.plugins.RegisterObjectPlugin(id=PLUGIN_ID,
                                 str="quick_stitch",
                                 g=QuickStitch,
                                 description="quick_stitch",
                                 icon=bmp,
                                 info=c4d.OBJECT_POLYGONOBJECT)