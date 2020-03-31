CONTAINER quick_stitch
{
    NAME quick_stitch;
    INCLUDE Obase;

    GROUP ID_OBJECTPROPERTIES
    {
        BUTTON QUICK_STITCH_BUTTON      {}
        LINK   QUICK_STITCH_SOURCE      {}
        LONG   QUICK_STITCH_COUNT       {}
        //REAL   QUICK_STITCH_STEP        { UNIT METER; }
        REAL   QUICK_STITCH_WIDTH       { UNIT METER; }
        REAL   QUICK_STITCH_HEIGHT      { UNIT METER; }
        REAL   QUICK_STITCH_THICKNESS   { UNIT METER; }
        REAL   QUICK_STITCH_OFFSET      { UNIT METER; }
        SPLINE QUICK_STITCH_SHAPE       {}
    }

    INCLUDE Oprimitiveaxis;
}
