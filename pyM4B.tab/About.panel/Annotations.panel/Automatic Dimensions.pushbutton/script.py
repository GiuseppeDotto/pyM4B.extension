from pyrevit import DB, revit, script, forms


doc = revit.doc
uidoc = revit.uidoc
logger = script.get_logger()


def mm_to_internal(value):
    if int(doc.Application.VersionNumber) < 2022:
        return DB.UnitUtils.ConvertToInternalUnits(value, DB.DisplayUnitType.DUT_MILLIMETERS)
    return DB.UnitUtils.ConvertToInternalUnits(value, DB.UnitTypeId.Millimeters)


def is_2d_view(view):
    allowed = (
        DB.ViewType.FloorPlan,
        DB.ViewType.CeilingPlan,
        DB.ViewType.EngineeringPlan,
        DB.ViewType.AreaPlan,
        DB.ViewType.Section,
        DB.ViewType.Elevation,
        DB.ViewType.Detail,
    )
    return (not view.IsTemplate) and view.ViewType in allowed


def select_view3d():
    views3d = [
        v
        for v in DB.FilteredElementCollector(doc).OfClass(DB.View3D)
        if not v.IsTemplate
    ]
    if not views3d:
        forms.alert("No 3D views available.", exitscript=True)
    view3d = forms.SelectFromList.show(
        views3d,
        name_attr="Name",
        title="Select 3D View (ReferenceIntersector)",
        multiselect=False,
    )
    if not view3d:
        script.exit()
    return view3d


def select_view2d():
    active_view = doc.ActiveView
    choice = forms.CommandSwitchWindow.show(
        ["Use Active View", "Pick 2D View"],
        message="Select the 2D view where dimensions will be created.",
    )
    if not choice:
        script.exit()
    if choice == "Use Active View":
        if not is_2d_view(active_view):
            forms.alert("Active view is not a valid 2D view.", exitscript=True)
        return active_view

    views2d = [
        v
        for v in DB.FilteredElementCollector(doc).OfClass(DB.View)
        if is_2d_view(v)
    ]
    if not views2d:
        forms.alert("No valid 2D views available.", exitscript=True)
    view2d = forms.SelectFromList.show(
        views2d,
        name_attr="Name",
        title="Select 2D View (Dimension View)",
        multiselect=False,
    )
    if not view2d:
        script.exit()
    return view2d


def select_dimension_type():
    dim_types = list(DB.FilteredElementCollector(doc).OfClass(DB.DimensionType))
    if not dim_types:
        forms.alert("No dimension types found.", exitscript=True)
    name_map = {}
    for dt in dim_types:
        name = dt.Name
        if name in name_map:
            name = "{} [{}]".format(name, dt.Id.IntegerValue)
        name_map[name] = dt
    selection = forms.SelectFromList.show(
        sorted(name_map.keys()),
        title="Select Dimension Type",
        multiselect=False,
    )
    if not selection:
        script.exit()
    return name_map[selection]


def build_intersector(view3d):
    cats = [
        DB.BuiltInCategory.OST_Walls,
        DB.BuiltInCategory.OST_CurtainWallPanels,
        DB.BuiltInCategory.OST_Doors,
    ]
    filters = [DB.ElementCategoryFilter(c) for c in cats]
    cat_filter = DB.LogicalOrFilter(filters)
    intersector = DB.ReferenceIntersector(
        cat_filter, DB.FindReferenceTarget.Face, view3d
    )
    intersector.FindReferencesInRevitLinks = False
    return intersector


def find_ref(intersector, origin, direction):
    hit = intersector.FindNearest(origin, direction)
    if hit:
        return hit.GetReference()
    return None


view3d = select_view3d()
view2d = select_view2d()
dim_type = select_dimension_type()

rooms = (
    DB.FilteredElementCollector(doc, view2d.Id)
    .OfCategory(DB.BuiltInCategory.OST_Rooms)
    .WhereElementIsNotElementType()
    .ToElements()
)
if not rooms:
    forms.alert("No rooms found in the selected 2D view.", exitscript=True)

intersector = build_intersector(view3d)
right = view2d.RightDirection.Normalize()
up = view2d.UpDirection.Normalize()
offset = mm_to_internal(200.0)

created = 0
skipped = 0

with revit.Transaction("Automatic Room Dimensions"):
    for room in rooms:
        if room.Area <= 0:
            skipped += 1
            continue

        bbox = room.get_BoundingBox(view2d)
        if not bbox:
            skipped += 1
            continue

        t = bbox.Transform
        bbmin = bbox.Min
        bbmax = bbox.Max
        width = bbmax.X - bbmin.X
        height = bbmax.Y - bbmin.Y
        if width <= 0 or height <= 0:
            skipped += 1
            continue

        midz = (bbmin.Z + bbmax.Z) * 0.5
        eps = max(0.01, 0.05 * min(width, height))
        origin = t.OfPoint(DB.XYZ(bbmin.X + eps, bbmin.Y + eps, midz))

        ref_left = find_ref(intersector, origin, -right)
        ref_right = find_ref(intersector, origin, right)
        ref_down = find_ref(intersector, origin, -up)
        ref_up = find_ref(intersector, origin, up)

        if not (ref_left and ref_right and ref_down and ref_up):
            skipped += 1
            continue

        p1 = t.OfPoint(DB.XYZ(bbmin.X, bbmin.Y, midz)) - (up * offset)
        p2 = t.OfPoint(DB.XYZ(bbmax.X, bbmin.Y, midz)) - (up * offset)
        p3 = t.OfPoint(DB.XYZ(bbmin.X, bbmin.Y, midz)) - (right * offset)
        p4 = t.OfPoint(DB.XYZ(bbmin.X, bbmax.Y, midz)) - (right * offset)

        line_h = DB.Line.CreateBound(p1, p2)
        line_v = DB.Line.CreateBound(p3, p4)

        refs_h = DB.ReferenceArray()
        refs_h.Append(ref_left)
        refs_h.Append(ref_right)

        refs_v = DB.ReferenceArray()
        refs_v.Append(ref_down)
        refs_v.Append(ref_up)

        dim_h = doc.Create.NewDimension(view2d, line_h, refs_h)
        dim_v = doc.Create.NewDimension(view2d, line_v, refs_v)
        if dim_h and dim_type:
            dim_h.DimensionType = dim_type
        if dim_v and dim_type:
            dim_v.DimensionType = dim_type
        created += 1

logger.info("Rooms processed: %s | Dimensions created: %s | Skipped: %s", len(rooms), created, skipped)
