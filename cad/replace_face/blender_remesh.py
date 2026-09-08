#!/usr/bin/env python3
"""Clean one-body replace-face STLs in Blender and export printables.

Preferred (headless / CI-friendly if Blender is installed):

    blender --background --python cad/replace_face/blender_remesh.py

System Python re-execs Blender when ``bpy`` is missing:

    python3 cad/replace_face/blender_remesh.py

This script does **not** invent geometry. OpenSCAD (``dims.scad``) stays the
parametric source of truth. Callipers are still PLACEHOLDER. Not a verified
AP1 drop-in.

Per part (one solid per file — tray and web are never merged):

- millimetre units; origin stays at (0, 0, 0)
- face parts: origin = bottom-left of the 170 × 72.3 face box
- buttons: keep their local SCAD origin
- merge-by-distance, delete loose, dissolve degenerates
- consistent outward normals
- fill only tiny non-manifold holes if any (≤ 4 sides)
- no voxel remesh (would chew the parabola arch / notches)
- no stems, clips, pin bosses, or Honda connector pitch
"""

from __future__ import annotations

import os
import shutil
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
RAW_STL = HERE / "stl"
PRINT_STL = HERE / "print" / "stl"
PRINT_STEP = HERE / "print" / "step"
PRINT_OBJ = HERE / "print" / "obj"
PREVIEW = HERE / "preview"

# One body per file — do not add a combined tray+web solid.
FACE_PARTS = ("backlight", "backlight_web", "acrylic_face")
BUTTON_PARTS = ("button_rocker", "button_sel", "button_trip")
PARTS = FACE_PARTS + BUTTON_PARTS

# Assembly placement copies dims.scad / assembly.scad. Do not invent sizes.
FACE_W = 170.0
FACE_H = 72.3
BTN_PAD_X_PCT = 0.018
ROCKER_W_PCT = 0.092
TRIP_W_PCT = 0.062
LAMP_Y_PCT = 0.805
BEZEL_H_PCT = 0.175
BTN_H_FROM_BEZEL = 0.48
SEL_GAP_MM = 1.0
FLOOR_T = 1.6
FACE_T = 2.0
TRAY_H = 12.0
FACE_REBATE_Z = TRAY_H - FACE_T
BUTTON_CAP_T = 2.4
EXPLODE_MM = 14.0  # same air gap as assembly.scad (not a fit claim)

# Conservative weld — well below print tolerance; keeps the locked outline.
WELD_MM = 1.0e-4
DEGENERATE_MM = 1.0e-4


def _argv_user() -> list[str]:
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1 :]
    if sys.argv and Path(sys.argv[0]).name == "blender":
        return []
    return sys.argv[1:]


def _print_help() -> None:
    sys.stdout.write(
        "Clean replace-face STLs and export print/ + preview/\n\n"
        "  blender --background --python cad/replace_face/blender_remesh.py\n"
        "  python3 cad/replace_face/blender_remesh.py\n\n"
        "Options:\n"
        "  --help     this text (no Blender required)\n"
        "  --check    import bpy / find blender, then exit\n"
    )


def _ensure_bpy() -> None:
    try:
        import bpy  # noqa: F401

        return
    except ImportError:
        pass

    blender = os.environ.get("BLENDER") or shutil.which("blender")
    if blender is None:
        sys.stderr.write(
            "Blender not found (no bpy, no blender on PATH).\n"
            "Install Blender 4.x and run:\n"
            f"  blender --background --python {HERE / 'blender_remesh.py'}\n"
        )
        raise SystemExit(2)

    script = str(Path(__file__).resolve())
    user = _argv_user()
    cmd = [blender, "--background", "--python", script]
    if user:
        cmd += ["--", *user]
    if not os.environ.get("DISPLAY") and shutil.which("xvfb-run"):
        cmd = ["xvfb-run", "-a", *cmd]
    os.execvp(cmd[0], cmd)


def _clear_scene(bpy) -> None:
    # Do not call read_factory_settings — it can abort a --python script.
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="SELECT")
    if bpy.context.selected_objects:
        bpy.ops.object.delete(use_global=False)
    for collection in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(collection):
            collection.remove(block)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "MILLIMETERS"


def _import_stl(bpy, path: Path):
    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(
            filepath=str(path),
            global_scale=1.0,
            use_scene_unit=False,
            forward_axis="Y",
            up_axis="Z",
            use_mesh_validate=True,
        )
    else:
        bpy.ops.import_mesh.stl(
            filepath=str(path),
            global_scale=1.0,
            use_scene_unit=False,
            axis_forward="Y",
            axis_up="Z",
        )
    obj = bpy.context.view_layer.objects.active
    if obj is None or obj.type != "MESH":
        selected = [o for o in bpy.context.selected_objects if o.type == "MESH"]
        if not selected:
            raise RuntimeError(f"STL import produced no mesh: {path}")
        obj = selected[0]
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)
    return obj


def _mesh_stats(obj) -> dict:
    mesh = obj.data
    bbox = [tuple(obj.bound_box[i]) for i in range(8)]
    xs = [p[0] for p in bbox]
    ys = [p[1] for p in bbox]
    zs = [p[2] for p in bbox]
    return {
        "name": obj.name,
        "verts": len(mesh.vertices),
        "faces": len(mesh.polygons),
        "bbox_min": (min(xs), min(ys), min(zs)),
        "bbox_max": (max(xs), max(ys), max(zs)),
    }


def _clean_mesh(bpy, obj) -> dict:
    """Manifold hygiene only. No remesh unless a hole actually exists."""
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=WELD_MM)
    bpy.ops.mesh.delete_loose()
    bpy.ops.mesh.dissolve_degenerate(threshold=DEGENERATE_MM)
    bpy.ops.mesh.normals_make_consistent(inside=False)

    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.mesh.select_non_manifold()
    # 4.0 has no "selected face count" op that is reliable here; try a
    # conservative hole fill. No-op when nothing non-manifold is selected.
    bpy.ops.mesh.fill_holes(sides=4)
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.shade_flat()
    obj.location = (0.0, 0.0, 0.0)
    return _mesh_stats(obj)


def _export_stl(bpy, obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_mesh.stl(
        filepath=str(path),
        use_selection=True,
        global_scale=1.0,
        use_scene_unit=False,
        ascii=False,
        use_mesh_modifiers=True,
        axis_forward="Y",
        axis_up="Z",
    )


def _export_obj(bpy, obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.obj_export(
        filepath=str(path),
        export_selected_objects=True,
        apply_modifiers=True,
        export_materials=False,
        export_uv=False,
        export_normals=True,
        export_triangulated_mesh=True,
        forward_axis="Y",
        up_axis="Z",
        global_scale=1.0,
    )


def _mesh_world_triangles(obj):
    mesh = obj.data
    verts = [tuple(v.co) for v in mesh.vertices]
    faces = []
    for poly in mesh.polygons:
        vid = list(poly.vertices)
        if len(vid) < 3:
            continue
        for i in range(1, len(vid) - 1):
            faces.append((vid[0], vid[i], vid[i + 1]))
    return verts, faces


def _step_real(value: float) -> str:
    text = f"{value:.8f}".rstrip("0").rstrip(".")
    if text in {"-0", ""}:
        return "0."
    if "." not in text:
        text += "."
    return text


def write_faceted_step(path: Path, verts, faces, part_name: str) -> None:
    """Write a millimetre FACETED_BREP STEP.

    Blender cannot emit parametric STEP/NURBS. This is an honest tessellation
    of the cleaned mesh (same triangles as the printable STL), not a B-rep
    rebuild and not a measured AP1 solid.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    safe = part_name.replace("'", "''")

    lines = [
        "ISO-10303-21;",
        "HEADER;",
        "FILE_DESCRIPTION(('replace-face cleaned mesh - faceted PLACEHOLDER,"
        " not parametric CAD, not a verified AP1 drop-in'),'2;1');",
        f"FILE_NAME('{path.name}','{now}',('s2000-ap1-digital-dash'),(''),"
        f"'cad/replace_face/blender_remesh.py','s2000-ap1-digital-dash','');",
        "FILE_SCHEMA(('CONFIG_CONTROL_DESIGN'));",
        "ENDSEC;",
        "DATA;",
        "#1=APPLICATION_CONTEXT('configuration controlled 3d designs of "
        "mechanical parts and assemblies');",
        "#2=APPLICATION_PROTOCOL_DEFINITION('international standard',"
        "'config_control_design',1994,#1);",
        "#3=PRODUCT_CONTEXT('',#1,'mechanical');",
        f"#4=PRODUCT('{safe}','{safe}','PLACEHOLDER faceted mesh - "
        "OpenSCAD remains source of truth',(#3));",
        "#5=PRODUCT_DEFINITION_FORMATION('','',#4);",
        "#6=PRODUCT_DEFINITION_CONTEXT('part definition',#1,'design');",
        "#7=PRODUCT_DEFINITION('design','',#5,#6);",
        "#8=PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,(#4));",
        "#9=PRODUCT_DEFINITION_SHAPE('','',#7);",
        "#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));",
        "#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));",
        "#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());",
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-6),#10,"
        "'distance_accuracy_value','confusion accuracy');",
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
        "GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))"
        "GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))"
        "REPRESENTATION_CONTEXT('Context #1',"
        "'3D Context with UNIT and UNCERTAINTY'));",
    ]

    eid = 20
    point_ids: list[int] = []
    for x, y, z in verts:
        lines.append(
            f"#{eid}=CARTESIAN_POINT('',({_step_real(x)},{_step_real(y)},"
            f"{_step_real(z)}));"
        )
        point_ids.append(eid)
        eid += 1

    face_ids: list[int] = []
    for a, b, c in faces:
        pa, pb, pc = (verts[a], verts[b], verts[c])
        ux, uy, uz = pb[0] - pa[0], pb[1] - pa[1], pb[2] - pa[2]
        vx, vy, vz = pc[0] - pa[0], pc[1] - pa[1], pc[2] - pa[2]
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        nlen = (nx * nx + ny * ny + nz * nz) ** 0.5
        if nlen < 1e-12:
            continue
        nx, ny, nz = nx / nlen, ny / nlen, nz / nlen
        ulen = (ux * ux + uy * uy + uz * uz) ** 0.5
        if ulen < 1e-12:
            continue
        rx, ry, rz = ux / ulen, uy / ulen, uz / ulen

        origin_id = eid
        lines.append(
            f"#{eid}=CARTESIAN_POINT('',({_step_real(pa[0])},"
            f"{_step_real(pa[1])},{_step_real(pa[2])}));"
        )
        eid += 1
        n_id = eid
        lines.append(
            f"#{eid}=DIRECTION('',({_step_real(nx)},{_step_real(ny)},"
            f"{_step_real(nz)}));"
        )
        eid += 1
        r_id = eid
        lines.append(
            f"#{eid}=DIRECTION('',({_step_real(rx)},{_step_real(ry)},"
            f"{_step_real(rz)}));"
        )
        eid += 1
        axis_id = eid
        lines.append(f"#{eid}=AXIS2_PLACEMENT_3D('',#{origin_id},#{n_id},#{r_id});")
        eid += 1
        plane_id = eid
        lines.append(f"#{eid}=PLANE('',#{axis_id});")
        eid += 1
        loop_id = eid
        lines.append(
            f"#{eid}=POLY_LOOP('',(#{point_ids[a]},#{point_ids[b]},"
            f"#{point_ids[c]}));"
        )
        eid += 1
        bound_id = eid
        lines.append(f"#{eid}=FACE_OUTER_BOUND('',#{loop_id},.T.);")
        eid += 1
        face_id = eid
        lines.append(f"#{eid}=FACE_SURFACE('',(#{bound_id}),#{plane_id},.T.);")
        face_ids.append(face_id)
        eid += 1

    if not face_ids:
        raise RuntimeError(f"no triangles for STEP: {part_name}")

    shell_id = eid
    face_list = ",".join(f"#{i}" for i in face_ids)
    lines.append(f"#{shell_id}=CLOSED_SHELL('',({face_list}));")
    eid += 1
    brep_id = eid
    lines.append(f"#{brep_id}=FACETED_BREP('{safe}',#{shell_id});")
    eid += 1
    repr_id = eid
    lines.append(
        f"#{repr_id}=ADVANCED_BREP_SHAPE_REPRESENTATION('',(#{brep_id}),#14);"
    )
    eid += 1
    lines.append(f"#{eid}=SHAPE_DEFINITION_REPRESENTATION(#9,#{repr_id});")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def _button_xy() -> dict[str, tuple[float, float]]:
    rocker_x = FACE_W * BTN_PAD_X_PCT
    trip_w = FACE_W * TRIP_W_PCT
    trip_x = FACE_W - FACE_W * BTN_PAD_X_PCT - trip_w
    sel_x = trip_x - trip_w - SEL_GAP_MM
    bezel_h = FACE_H * BEZEL_H_PCT
    btn_h = bezel_h * BTN_H_FROM_BEZEL
    btn_y_from_top = FACE_H * LAMP_Y_PCT + (bezel_h - btn_h) / 2.0
    btn_y = FACE_H - btn_y_from_top - btn_h
    return {
        "button_rocker": (rocker_x, btn_y),
        "button_sel": (sel_x, btn_y),
        "button_trip": (trip_x, btn_y),
    }


def _make_material(bpy, name: str, rgba: tuple[float, float, float, float]):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        raise RuntimeError("Principled BSDF missing")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = 0.45
    if rgba[3] < 0.99:
        bsdf.inputs["Alpha"].default_value = rgba[3]
        mat.blend_method = "BLEND"
    return mat


def _place_assembly(bpy, objects: dict) -> None:
    # Colours match assembly.scad (exploded preview, not a fit claim).
    materials = {
        "backlight": _make_material(bpy, "tray_petg", (0.22, 0.22, 0.24, 1.0)),
        "backlight_web": _make_material(bpy, "web_petg", (0.55, 0.52, 0.48, 1.0)),
        "acrylic_face": _make_material(
            bpy, "acrylic_mask", (0.82, 0.80, 0.74, 0.55)
        ),
        "button_rocker": _make_material(bpy, "tpu_button", (0.12, 0.12, 0.12, 1.0)),
        "button_sel": _make_material(bpy, "tpu_button_sel", (0.12, 0.12, 0.12, 1.0)),
        "button_trip": _make_material(bpy, "tpu_button_trip", (0.12, 0.12, 0.12, 1.0)),
    }
    objects["backlight"].location = (0.0, 0.0, 0.0)
    objects["backlight_web"].location = (0.0, 0.0, FLOOR_T + EXPLODE_MM * 0.35)
    objects["acrylic_face"].location = (0.0, 0.0, FACE_REBATE_Z + EXPLODE_MM)

    btn_z = TRAY_H + EXPLODE_MM * 2.0 + BUTTON_CAP_T * 0.35
    for name, (x, y) in _button_xy().items():
        obj = objects[name]
        obj.location = (x, y, btn_z)
        obj.scale = (1.0, 1.0, -1.0)

    for name, obj in objects.items():
        obj.data.materials.clear()
        obj.data.materials.append(materials[name])
        obj.name = name


def _export_glb(bpy, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # glTF is metres. Vertices are stored as millimetres (1 BU = 1 mm).
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.scale = (
                obj.scale[0] * 0.001,
                obj.scale[1] * 0.001,
                obj.scale[2] * 0.001,
            )
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        export_copyright=(
            "PLACEHOLDER replace-face preview — not a verified AP1 drop-in"
        ),
        export_yup=True,
        export_apply=True,
        export_animations=False,
        export_skins=False,
        export_morph=False,
        export_lights=False,
        export_cameras=False,
        export_texcoords=False,
        export_draco_mesh_compression_enable=False,
        use_selection=False,
    )


def _verify_binary_stl(path: Path) -> int:
    data = path.read_bytes()
    if len(data) < 84:
        raise RuntimeError(f"STL too small: {path}")
    count = struct.unpack_from("<I", data, 80)[0]
    expected = 84 + count * 50
    if expected != len(data):
        raise RuntimeError(
            f"STL not binary or size mismatch: {path} "
            f"(hdr={count} bytes={len(data)} expected={expected})"
        )
    return count


def run() -> int:
    import bpy

    if not RAW_STL.is_dir():
        sys.stderr.write(f"missing raw STLs: {RAW_STL}\n")
        return 2

    _clear_scene(bpy)
    objects = {}

    for part in PARTS:
        src = RAW_STL / f"{part}.stl"
        if not src.is_file():
            sys.stderr.write(f"missing {src}\n")
            return 2
        obj = _import_stl(bpy, src)
        obj.name = part
        stats = _clean_mesh(bpy, obj)
        objects[part] = obj

        stl_out = PRINT_STL / f"{part}.stl"
        _export_stl(bpy, obj, stl_out)
        tris = _verify_binary_stl(stl_out)

        verts, faces = _mesh_world_triangles(obj)
        write_faceted_step(PRINT_STEP / f"{part}.step", verts, faces, part)
        _export_obj(bpy, obj, PRINT_OBJ / f"{part}.obj")

        line = (
            f"{part}: verts={stats['verts']} faces={stats['faces']} "
            f"stl_tris={tris} "
            f"bbox={stats['bbox_min']} → {stats['bbox_max']}"
        )
        print(line)

    _place_assembly(bpy, objects)
    glb = PREVIEW / "assembly.glb"
    _export_glb(bpy, glb)
    print(f"preview: {glb} ({glb.stat().st_size} bytes)")
    print("materials: PETG/ASA hard parts, TPU buttons, no PLA")
    print("status: PLACEHOLDER — callipers required; not a verified AP1 drop-in")
    return 0


def main() -> int:
    user = _argv_user()
    if "--help" in user or "-h" in user:
        _print_help()
        return 0
    if "--check" in user:
        _ensure_bpy()
        import bpy

        print(f"bpy {bpy.app.version_string}")
        return 0
    _ensure_bpy()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
