
import os
import sys
import c4d
import copy

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

            pos[0] = (pos[0] - 0.5) * width
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
        arc[c4d.SPLINEOBJECT_ANGLE] = c4d.utils.DegToRad(15)
        
def create_spline_from_obj(node, obj):
    if (not obj) or (not obj.CheckType(c4d.Opolygon)):
        print "obj is None(create_spline)"
        return True

    source = obj.GetClone()
    selected = source.GetEdgeS()
    count = selected.GetCount()
    if count < 1:
        return True
    if c4d.utils.SendModelingCommand(c4d.MCOMMAND_EDGE_TO_SPLINE, [source]):
        spl = source.GetDown().GetClone()
        spl[c4d.SPLINEOBJECT_INTERPOLATION] = 2 # uniform
        copy_coordnates(obj, spl)
        spl.InsertUnder(node)
        source.GetDown().Remove()

def copy_coordnates(from_obj, to_obj):
    to_obj.SetMg(from_obj.GetMg())



class QuickStitch(c4d.plugins.ObjectData):
    def __init__(self, *args):
        self.SetOptimizeCache(True)

    def Init(self, op):
        self.InitAttr(op, int,   c4d.QUICK_STITCH_COUNT)
        self.InitAttr(op, float, c4d.QUICK_STITCH_WIDTH)
        self.InitAttr(op, float, c4d.QUICK_STITCH_HEIGHT)
        self.InitAttr(op, float, c4d.QUICK_STITCH_THICKNESS)
        self.InitAttr(op, float, c4d.QUICK_STITCH_OFFSET)
        self.InitAttr(op, float, c4d.QUICK_STITCH_ROTATION_H)
        self.InitAttr(op, float, c4d.QUICK_STITCH_ROTATION_B)
        self.InitAttr(op, float, c4d.QUICK_STITCH_ROTATION_P)

        op[c4d.QUICK_STITCH_COUNT] = 100
        op[c4d.QUICK_STITCH_WIDTH] = 6.0
        op[c4d.QUICK_STITCH_HEIGHT] = 3.0
        op[c4d.QUICK_STITCH_THICKNESS] = 0.5
        op[c4d.QUICK_STITCH_OFFSET] = -1.0
        op[c4d.QUICK_STITCH_ROTATION_H] = 0.0
        op[c4d.QUICK_STITCH_ROTATION_B] = 0.0
        op[c4d.QUICK_STITCH_ROTATION_P] = 0.0

        # init spline data
        spd = c4d.SplineData()
        spd.MakePointBuffer(3)
        spd.SetKnot(0, c4d.Vector(0.0, 0.0, 0.0), 65536, vTangentRight=c4d.Vector(0.0, 0.5, 0.0), interpol=0)
        spd.SetKnot(1, c4d.Vector(0.5, 1.0, 0.0), 131072, vTangentLeft=c4d.Vector(-0.25, 0.0, 0.0), vTangentRight=c4d.Vector(0.25, 0.0, 0.0), interpol=0)
        spd.SetKnot(2, c4d.Vector(1.0, 0.0, 0.0), 196608, vTangentLeft=c4d.Vector(0.0, 0.5, 0.0), interpol=0)
        op[c4d.QUICK_STITCH_SHAPE] = spd

        # # create
        self.spline = None
        self.null = c4d.BaseObject(c4d.Onull)
        self.cloner  = c4d.BaseObject(CLONER_OBJECT)

        return True

    def set_spline(self, spline):
        if not spline.IsAlive():
            print "DEAD: spline(set_spline)"
            spline = None
            return
        self.spline = spline.GetClone()
        self.spline.InsertUnder(self.null)
        self.cloner[c4d.MG_OBJECT_LINK] = self.spline
    

    def Message(self, node, type, data):
        if type == c4d.MSG_DESCRIPTION_COMMAND:
            if data["id"][0].id != c4d.QUICK_STITCH_BUTTON:
                return True

            create_spline_from_obj(node, self.obj)


        return True        

    def GetVirtualObjects(self, op, hierarchyhelp):

        # create
        self.obj = op[c4d.QUICK_STITCH_SOURCE]
        self.arc = c4d.SplineObject(1, c4d.SPLINETYPE_BEZIER)
        self.null = c4d.BaseObject(c4d.Onull)
        self.sweep = c4d.BaseObject(c4d.Osweep)
        self.sweep.SetPhong(True, True, c4d.utils.DegToRad(50))
        self.circle = c4d.BaseObject(c4d.Osplinecircle)
        self.cloner  = c4d.BaseObject(CLONER_OBJECT)

        # insert
        self.arc.InsertUnder(self.sweep)
        self.circle.InsertUnder(self.sweep)
        self.sweep.InsertUnder(self.cloner)
        self.cloner.InsertUnder(self.null)

        # get obj
        self.obj = op[c4d.QUICK_STITCH_SOURCE]

        # get spline
        if not op.GetDown():
            print "spline is None"
            return None    
        self.spline = op.GetDown()

        # property
        count = op[c4d.QUICK_STITCH_COUNT]
        width = op[c4d.QUICK_STITCH_WIDTH]
        height = op[c4d.QUICK_STITCH_HEIGHT]
        thickness = op[c4d.QUICK_STITCH_THICKNESS]
        offset = op[c4d.QUICK_STITCH_OFFSET]
        rotation_h = op[c4d.QUICK_STITCH_ROTATION_H]
        rotation_b = op[c4d.QUICK_STITCH_ROTATION_B]
        rotation_p = op[c4d.QUICK_STITCH_ROTATION_P]

        # circle
        self.circle[c4d.PRIM_CIRCLE_RADIUS] = thickness
        self.circle[c4d.SPLINEOBJECT_SUB] = 1

        # shape
        self.shape = op[c4d.QUICK_STITCH_SHAPE]
        create_spline_from_splinedata(self.shape, self.arc, width, height)

        # cloner setting
        self.cloner[c4d.ID_MG_MOTIONGENERATOR_MODE] = 0              # object
        self.cloner[c4d.MG_SPLINE_MODE] = 0                          # count
        self.cloner[c4d.MG_SPLINE_COUNT] = count
        self.cloner[c4d.ID_MG_TRANSFORM_POSITION,c4d.VECTOR_X] = -offset
        self.cloner[c4d.ID_MG_TRANSFORM_ROTATE,c4d.VECTOR_X] = rotation_h
        self.cloner[c4d.ID_MG_TRANSFORM_ROTATE,c4d.VECTOR_Y] = rotation_p
        self.cloner[c4d.ID_MG_TRANSFORM_ROTATE,c4d.VECTOR_Z] = rotation_b
        self.cloner[c4d.MG_OBJECT_LINK] = self.spline

        return self.null

    def CopyTo(self, dest, snode, dnode, flags, trn):
        if snode.GetDown():
            self.spline = snode.GetDown()
        if self.spline:
            dest.set_spline(self.spline)
        return True


if __name__ == "__main__":
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "qiuckstitch.tif")

    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    c4d.plugins.RegisterObjectPlugin(id=PLUGIN_ID,
                                 str="QuickStitch",
                                 g=QuickStitch,
                                 description="quick_stitch",
                                 icon=bmp,
                                 info=c4d.OBJECT_GENERATOR)
