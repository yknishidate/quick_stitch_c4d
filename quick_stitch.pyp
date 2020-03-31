
import os
import sys
import c4d

PLUGIN_ID = 1054816
CLONER_OBJECT = 1018544
MOSPLINE_OBJECT = 440000054



def create_spline_from_splinedata(spData, arc, width, height):
        if not spData:
            return 
        knots = spData.GetKnots()
        cnt = len(knots)
        arc.ResizeObject(cnt)
        for i in xrange(cnt):
            pos = knots[i]["vPos"]
            tan_r = knots[i]["vTangentRight"]
            tan_l = knots[i]["vTangentLeft"]

            pos[0] *= width
            pos[1] *= height
            tan_r[0] *= width
            tan_r[1] *= height
            tan_l[0] *= width
            tan_l[1] *= height

            arc.SetPoint(i, pos)
            arc.SetTangent(i, tan_l, tan_r)
        arc[c4d.SPLINEOBJECT_ANGLE] = c4d.utils.DegToRad(10)
        arc[c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_X] = c4d.utils.DegToRad(-90)
        arc[c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_Y] = c4d.utils.DegToRad(90)
        

class QuickStitch(c4d.plugins.ObjectData):
    def __init__(self, *args):
        super(QuickStitch, self).__init__(*args)
        self.SetOptimizeCache(True)

    def Init(self, op):
        self.InitAttr(op, int,   c4d.QUICK_STITCH_COUNT)
        self.InitAttr(op, float, c4d.QUICK_STITCH_WIDTH)
        self.InitAttr(op, float, c4d.QUICK_STITCH_HEIGHT)
        self.InitAttr(op, float, c4d.QUICK_STITCH_THICKNESS)
        self.InitAttr(op, float, c4d.QUICK_STITCH_OFFSET)

        op[c4d.QUICK_STITCH_COUNT] = 50
        op[c4d.QUICK_STITCH_WIDTH] = 10.0
        op[c4d.QUICK_STITCH_HEIGHT] = 5.0
        op[c4d.QUICK_STITCH_THICKNESS] = 2.0

        # --------------------------------------------------
        spd = c4d.SplineData()
        spd.MakePointBuffer(3)
        spd.SetKnot(0, c4d.Vector(0.0, 0.0, 0.0), 65536, vTangentRight=c4d.Vector(0.0, 0.5, 0.0), interpol=0)
        spd.SetKnot(1, c4d.Vector(0.5, 1.0, 0.0), 131072, vTangentLeft=c4d.Vector(-0.25, 0.0, 0.0), vTangentRight=c4d.Vector(0.25, 0.0, 0.0), interpol=0)
        spd.SetKnot(0, c4d.Vector(1.0, 0.0, 0.0), 196608, vTangentLeft=c4d.Vector(0.0, 0.5, 0.0), interpol=0)
        op[c4d.QUICK_STITCH_SHAPE] = spd
        # --------------------------------------------------


        self.this = op

        # create
        self.obj = None
        self.shape = None
        self.spline = None
        self.arc = c4d.SplineObject(1, c4d.SPLINETYPE_BEZIER)
        self.null = c4d.BaseObject(c4d.Onull)
        self.sweep = c4d.BaseObject(c4d.Osweep)
        self.circle = c4d.BaseObject(c4d.Osplinecircle)
        self.cloner  = c4d.BaseObject(CLONER_OBJECT)

        # insert
        self.arc.InsertUnder(self.sweep)
        self.circle.InsertUnder(self.sweep)
        self.sweep.InsertUnder(self.cloner)
        self.cloner.InsertUnder(self.null)

        print "Init()"

        c4d.EventAdd()

        return True

    def Message(self, node, type, data):
        if type == c4d.MSG_DESCRIPTION_COMMAND:
            if data["id"][0].id != c4d.QUICK_STITCH_BUTTON:
                return True

            print "Message()"

            self.obj = self.this[c4d.QUICK_STITCH_SOURCE]
            if (not self.obj) or (not self.obj.CheckType(c4d.Opolygon)):
                return True

            source = self.obj.GetClone()
            selected = source.GetEdgeS()
            count = selected.GetCount()
            if count < 1:
                return True
            if c4d.utils.SendModelingCommand(c4d.MCOMMAND_EDGE_TO_SPLINE, [source]):
                self.spline = source.GetDown().GetClone()
                self.spline.InsertUnder(self.null)
                source.GetDown().Remove()
                self.cloner[c4d.MG_OBJECT_LINK] = self.spline

        return True        

    def GetVirtualObjects(self, op, hierarchyhelp):
        print "GetVirtualObjects()"
        # property
        count = op[c4d.QUICK_STITCH_COUNT]
        width = op[c4d.QUICK_STITCH_WIDTH]
        height = op[c4d.QUICK_STITCH_HEIGHT]
        thickness = op[c4d.QUICK_STITCH_THICKNESS]
        offset = op[c4d.QUICK_STITCH_OFFSET]

        # circle
        self.circle[c4d.PRIM_CIRCLE_RADIUS] = thickness
        self.circle[c4d.SPLINEOBJECT_SUB] = 2

        # shape
        self.shape = op[c4d.QUICK_STITCH_SHAPE]
        create_spline_from_splinedata(self.shape, self.arc, width, height)

        # cloner
        self.cloner[c4d.ID_MG_MOTIONGENERATOR_MODE] = 0              # object
        self.cloner[c4d.MG_SPLINE_MODE] = 0                          # count
        self.cloner[c4d.MG_SPLINE_COUNT] = count
        self.cloner[c4d.ID_MG_TRANSFORM_POSITION,c4d.VECTOR_X] = offset


        return self.null

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
                                 str="QuickStitch",
                                 g=QuickStitch,
                                 description="quick_stitch",
                                 icon=bmp,
                                 info=c4d.OBJECT_GENERATOR)
