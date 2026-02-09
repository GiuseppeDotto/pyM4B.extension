from pyrevit import DB, revit, script, forms


doc = revit.doc
uidoc = revit.uidoc
logger = script.get_logger()


def mm_to_internal(value):
    if int(doc.Application.VersionNumber) < 2022:
        return DB.UnitUtils.ConvertToInternalUnits(
            value, DB.DisplayUnitType.DUT_MILLIMETERS
        )
    return DB.UnitUtils.ConvertToInternalUnits(value, DB.UnitTypeId.Millimeters)


def get_element_name(elem):
    try:
        return DB.Element.Name.GetValue(elem)
    except Exception:
        pass
    try:
        return elem.Name
    except Exception:
        pass
    p = elem.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
    if p:
        n = p.AsString()
        if n:
            return n
    return "Element {}".format(elem.Id.IntegerValue)


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
        v for v in DB.FilteredElementCollector(doc).OfClass(DB.View) if is_2d_view(v)
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
    linear_types = []
    for dt in dim_types:
        try:
            if dt.StyleType == DB.DimensionStyleType.Linear:
                linear_types.append(dt)
        except Exception:
            continue

    dim_types = linear_types
    if not dim_types:
        forms.alert("No linear dimension types found.", exitscript=True)
    name_map = {}
    for dt in dim_types:
        name = get_element_name(dt)
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


def select_rooms(view2d):
    choice = forms.CommandSwitchWindow.show(
        ["All Rooms In View", "Only Selected Rooms"],
        message="Select which rooms to annotate.",
    )
    if not choice:
        script.exit()

    if choice == "Only Selected Rooms":
        selected_ids = list(uidoc.Selection.GetElementIds())
        rooms_sel = []
        for eid in selected_ids:
            elem = doc.GetElement(eid)
            if (
                elem
                and elem.Category
                and elem.Category.Id.IntegerValue == int(DB.BuiltInCategory.OST_Rooms)
            ):
                rooms_sel.append(elem)
        if not rooms_sel:
            with forms.WarningBar(title="select rooms to dimensions"):
                picked = revit.pick_elements_by_category(DB.BuiltInCategory.OST_Rooms)
            if not picked:
                script.exit()
            rooms_sel = list(picked)
        return rooms_sel

    rooms_all = (
        DB.FilteredElementCollector(doc, view2d.Id)
        .OfCategory(DB.BuiltInCategory.OST_Rooms)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    if not rooms_all:
        forms.alert("No rooms found in the selected 2D view.", exitscript=True)
    return rooms_all


def select_offset_mm(default_value=500.0):
    offset_str = forms.ask_for_string(
        default=str(default_value),
        prompt="Offset from wall (mm)",
        title="Dimension Offset",
    )
    if offset_str is None:
        script.exit()
    try:
        offset_val = float(offset_str)
    except Exception:
        forms.alert("Invalid offset value.", exitscript=True)
    if offset_val <= 0:
        forms.alert("Offset must be greater than 0.", exitscript=True)
    return offset_val


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


def get_room_center(room, view2d):
    bbox = room.get_BoundingBox(view2d)
    if not bbox:
        return None
    t = bbox.Transform
    bbmin = bbox.Min
    bbmax = bbox.Max
    mid = DB.XYZ(
        (bbmin.X + bbmax.X) * 0.5,
        (bbmin.Y + bbmax.Y) * 0.5,
        (bbmin.Z + bbmax.Z) * 0.5,
    )
    return t.OfPoint(mid)


def get_longest_edges(room, view2d, count=3):
    opts = DB.SpatialElementBoundaryOptions()
    try:
        opts.SpatialElementBoundaryLocation = DB.SpatialElementBoundaryLocation.Finish
    except Exception:
        pass
    loops = room.GetBoundarySegments(opts)
    if not loops:
        return []
    edges = []
    for loop in loops:
        for seg in loop:
            try:
                curve = seg.GetCurve()
            except Exception:
                continue
            if isinstance(curve, DB.Line):
                edges.append((curve, curve.Length))
    edges.sort(key=lambda x: x[1], reverse=True)
    return edges[:count]


def is_ref_parallel_to_dim(ref, dim_dir, hit_point):
    try:
        elem = doc.GetElement(ref.ElementId)
        if not elem:
            return True
        geom = elem.GetGeometryObjectFromReference(ref)
        if not isinstance(geom, DB.Face):
            return True
        proj = geom.Project(hit_point)
        if not proj:
            return True
        normal = geom.ComputeNormal(proj.UVPoint)
        if not normal:
            return True
        nd = normal.Normalize()
        dd = dim_dir.Normalize()
        return abs(nd.DotProduct(dd)) < 1e-3
    except Exception:
        return True


def make_detail_ref(hit_point, dim_dir, view2d, length_internal):
    half = length_internal * 0.5
    p1 = hit_point - (dim_dir * half)
    p2 = hit_point + (dim_dir * half)
    line = DB.Line.CreateBound(p1, p2)
    detail = doc.Create.NewDetailCurve(view2d, line)
    return detail.GeometryCurve.Reference


def create_dim_for_edge(
    edge_curve,
    center,
    view2d,
    intersector,
    offset_internal,
    dim_type,
    detail_len_internal,
):
    if not edge_curve:
        return False
    view_dir = view2d.ViewDirection.Normalize()
    dir_vec = edge_curve.Direction.Normalize()
    normal = dir_vec.CrossProduct(view_dir)
    if normal.GetLength() == 0:
        return False
    normal = normal.Normalize()

    p0 = edge_curve.GetEndPoint(0)
    p1 = edge_curve.GetEndPoint(1)
    mid = DB.XYZ(
        (p0.X + p1.X) * 0.5,
        (p0.Y + p1.Y) * 0.5,
        (p0.Z + p1.Z) * 0.5,
    )
    to_center = center - mid
    if to_center.DotProduct(normal) < 0:
        normal = -normal

    dim_center = mid + (normal * offset_internal)

    hit_pos = intersector.FindNearest(dim_center, normal)
    hit_neg = intersector.FindNearest(dim_center, -normal)
    if not (hit_pos and hit_neg):
        return False

    ref_pos = hit_pos.GetReference()
    ref_neg = hit_neg.GetReference()

    p_pos = dim_center + (normal * hit_pos.Proximity)
    p_neg = dim_center - (normal * hit_neg.Proximity)

    if not is_ref_parallel_to_dim(ref_pos, dir_vec, p_pos):
        ref_pos = make_detail_ref(p_pos, dir_vec, view2d, detail_len_internal)
    if not is_ref_parallel_to_dim(ref_neg, dir_vec, p_neg):
        ref_neg = make_detail_ref(p_neg, dir_vec, view2d, detail_len_internal)

    half = max(edge_curve.Length * 0.5, detail_len_internal)
    p1 = dim_center - (dir_vec * half)
    p2 = dim_center + (dir_vec * half)

    line = DB.Line.CreateBound(p1, p2)
    refs = DB.ReferenceArray()
    refs.Append(ref_pos)
    refs.Append(ref_neg)
    dim = doc.Create.NewDimension(view2d, line, refs)
    if dim and dim_type:
        dim.DimensionType = dim_type
    return True


view3d = select_view3d()
view2d = select_view2d()
dim_type = select_dimension_type()
offset_mm = select_offset_mm()

rooms = select_rooms(view2d)

intersector = build_intersector(view3d)
right = view2d.RightDirection.Normalize()
up = view2d.UpDirection.Normalize()
offset = mm_to_internal(offset_mm)
detail_len = mm_to_internal(50.0)

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
        center = t.OfPoint(
            DB.XYZ(
                (bbmin.X + bbmax.X) * 0.5,
                (bbmin.Y + bbmax.Y) * 0.5,
                midz,
            )
        )

        ref_left = find_ref(intersector, origin, -right)
        ref_right = find_ref(intersector, origin, right)
        ref_down = find_ref(intersector, origin, -up)
        ref_up = find_ref(intersector, origin, up)

        created_room = False
        if ref_left and ref_right and ref_down and ref_up:
            p1 = t.OfPoint(DB.XYZ(bbmin.X, bbmin.Y, midz)) + (up * offset)
            p2 = t.OfPoint(DB.XYZ(bbmax.X, bbmin.Y, midz)) + (up * offset)
            p3 = t.OfPoint(DB.XYZ(bbmin.X, bbmin.Y, midz)) + (right * offset)
            p4 = t.OfPoint(DB.XYZ(bbmin.X, bbmax.Y, midz)) + (right * offset)

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
            created_room = True
        else:
            edges = get_longest_edges(room, view2d, count=3)
            dims_made = 0
            for curve, seg_len in edges:
                if create_dim_for_edge(
                    curve,
                    center,
                    view2d,
                    intersector,
                    offset,
                    dim_type,
                    detail_len,
                ):
                    dims_made += 1
            if dims_made > 0:
                created_room = True
            else:
                skipped += 1
                continue
        if created_room:
            created += 1

logger.info(
    "Rooms processed: %s | Dimensions created: %s | Skipped: %s",
    len(rooms),
    created,
    skipped,
)
