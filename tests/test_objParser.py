"""Tests for objParser.

These pin both the public behaviour (triangulation, OBJ-spec quirks) and
the output format that downstream tools depend on byte-for-byte.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import objParser as op


def _run(tmp_path: Path, obj_text: str) -> tuple[int, str, str]:
    src = tmp_path / "in.obj"
    src.write_text(obj_text)
    v_out = tmp_path / "v.txt"
    t_out = tmp_path / "t.txt"
    tris = op.parse_obj(src, v_out, t_out)
    return tris, v_out.read_text(), t_out.read_text()


def test_quad_matches_legacy_byte_format(tmp_path):
    obj = textwrap.dedent(
        """\
        v 1.0 2.0 3.0
        v 4.0 5.0 6.0
        v 7.0 8.0 9.0
        v 10.0 11.0 12.0
        vt 0.1 0.2
        vt 0.3 0.4
        vt 0.5 0.6
        vt 0.7 0.8
        f 1/1 2/2 3/3 4/4
        """
    )
    tris, v, t = _run(tmp_path, obj)
    assert tris == 2
    assert v == (
        "1.0f*x, 2.0f*x, 3.0f*x, "
        "4.0f*x, 5.0f*x, 6.0f*x, "
        "7.0f*x, 8.0f*x, 9.0f*x, "
        "1.0f*x, 2.0f*x, 3.0f*x, "
        "7.0f*x, 8.0f*x, 9.0f*x, "
        "10.0f*x, 11.0f*x, 12.0f*x, "
    )
    assert t == (
        "0.1f, 0.2f, "
        "0.3f, 0.4f, "
        "0.5f, 0.6f, "
        "0.1f, 0.2f, "
        "0.5f, 0.6f, "
        "0.7f, 0.8f, "
    )


def test_triangle_emits_one_triangle(tmp_path):
    obj = (
        "v 1 1 1\nv 2 2 2\nv 3 3 3\n"
        "vt 0 0\nvt 0 0\nvt 0 0\n"
        "f 1/1 2/2 3/3\n"
    )
    tris, v, t = _run(tmp_path, obj)
    assert tris == 1
    assert v == "1f*x, 1f*x, 1f*x, 2f*x, 2f*x, 2f*x, 3f*x, 3f*x, 3f*x, "
    assert t == "0f, 0f, 0f, 0f, 0f, 0f, "


def test_pentagon_is_fan_triangulated(tmp_path):
    verts = "\n".join(f"v {i} {i} {i}" for i in range(1, 6))
    texs = "\n".join(["vt 0 0"] * 5)
    obj = f"{verts}\n{texs}\nf 1/1 2/2 3/3 4/4 5/5\n"
    tris, _, _ = _run(tmp_path, obj)
    assert tris == 3


def test_v_double_slash_vn_skips_textures(tmp_path):
    obj = "v 1 1 1\nv 2 2 2\nv 3 3 3\nf 1//1 2//2 3//3\n"
    tris, v, t = _run(tmp_path, obj)
    assert tris == 1
    assert v == "1f*x, 1f*x, 1f*x, 2f*x, 2f*x, 2f*x, 3f*x, 3f*x, 3f*x, "
    assert t == ""


def test_negative_indices_are_relative(tmp_path):
    obj = textwrap.dedent(
        """\
        v 1 1 1
        v 2 2 2
        v 3 3 3
        vt 0.1 0.1
        vt 0.2 0.2
        vt 0.3 0.3
        f -3/-3 -2/-2 -1/-1
        """
    )
    tris, v, t = _run(tmp_path, obj)
    assert tris == 1
    assert v == "1f*x, 1f*x, 1f*x, 2f*x, 2f*x, 2f*x, 3f*x, 3f*x, 3f*x, "
    assert t == "0.1f, 0.1f, 0.2f, 0.2f, 0.3f, 0.3f, "


def test_blank_lines_and_comments_are_ignored(tmp_path):
    obj = textwrap.dedent(
        """\
        # cube-like start

        v 1 1 1
        v 2 2 2
        v 3 3 3
        # another comment
        vt 0 0
        vt 0 0
        vt 0 0

        f 1/1 2/2 3/3
        """
    )
    tris, _, _ = _run(tmp_path, obj)
    assert tris == 1


def test_irrelevant_directives_are_ignored(tmp_path):
    obj = textwrap.dedent(
        """\
        mtllib foo.mtl
        o cube
        g geom
        s 1
        vn 0 0 1
        vp 0 0
        usemtl wood
        v 1 1 1
        v 2 2 2
        v 3 3 3
        vt 0 0
        vt 0 0
        vt 0 0
        f 1/1/1 2/2/1 3/3/1
        """
    )
    tris, _, _ = _run(tmp_path, obj)
    assert tris == 1


def test_stdout_message_format(tmp_path, capsys):
    obj = (
        "v 1 1 1\nv 2 2 2\nv 3 3 3\nv 4 4 4\n"
        "vt 0 0\nvt 0 0\nvt 0 0\nvt 0 0\n"
        "f 1/1 2/2 3/3 4/4\n"
    )
    _run(tmp_path, obj)
    out = capsys.readouterr().out
    assert "Total vertices: 6" in out
    assert "Total texture cordinates: 4" in out


def test_returns_triangle_count(tmp_path):
    obj = (
        "v 1 1 1\nv 2 2 2\nv 3 3 3\nv 4 4 4\nv 5 5 5\n"
        "vt 0 0\nvt 0 0\nvt 0 0\nvt 0 0\nvt 0 0\n"
        "f 1/1 2/2 3/3 4/4 5/5\n"
    )
    tris, _, _ = _run(tmp_path, obj)
    assert tris == 3


def test_main_cli_writes_outputs(tmp_path):
    src = tmp_path / "in.obj"
    src.write_text(
        "v 1 1 1\nv 2 2 2\nv 3 3 3\nv 4 4 4\n"
        "vt 0 0\nvt 0 0\nvt 0 0\nvt 0 0\n"
        "f 1/1 2/2 3/3 4/4\n"
    )
    v_out = tmp_path / "v.txt"
    t_out = tmp_path / "t.txt"
    assert op.main([str(src), str(v_out), str(t_out)]) == 0
    assert v_out.exists() and v_out.read_text().endswith("f*x, ")
    assert t_out.exists() and t_out.read_text().endswith("f, ")
