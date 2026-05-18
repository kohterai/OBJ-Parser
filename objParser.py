"""Cracked OBJ parser.

Reads a Wavefront ``.obj`` file and writes two text files containing the
per-vertex coordinates of the triangulated mesh, ready to upload to a
VBO and draw with ``glDrawArrays``.

Default input path, output paths, and output text format match the
original implementation byte-for-byte:

- ``finalVertex.txt``: each float suffixed with ``f*x, ``
- ``finalTexture.txt``: each float suffixed with ``f, ``
- stdout: ``Total vertices: N`` and ``Total texture cordinates: M``

Compared with the original, this version:

- Streams the input in a single pass and pre-formats each ``v`` / ``vt``
  on read, so triangulation collapses to index lookups and a single
  ``str.join`` per output file.
- Fan-triangulates faces of any size (the original handled quads only).
- Tolerates ``v//vn`` tokens with missing texture indices, comments,
  arbitrary whitespace, and OBJ-spec negative (relative) indices.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


def parse_obj(input_path: PathLike = "pear.obj",
              vertex_out_path: PathLike = "finalVertex.txt",
              texture_out_path: PathLike = "finalTexture.txt") -> int:
    """Parse ``input_path`` and write triangulated coordinate streams.

    Returns the number of output triangles.
    """
    vertex_strings: list[str] = []
    texture_strings: list[str] = []
    v_store = vertex_strings.append
    t_store = texture_strings.append

    v_out: list[str] = []
    t_out: list[str] = []
    v_emit = v_out.append
    t_emit = t_out.append

    triangle_count = 0

    with open(input_path, "r") as src:
        for raw in src:
            if raw.startswith("v "):
                p = raw.split()
                v_store(f"{p[1]}f*x, {p[2]}f*x, {p[3]}f*x, ")
            elif raw.startswith("vt "):
                p = raw.split()
                t_store(f"{p[1]}f, {p[2]}f, ")
            elif raw.startswith("f "):
                p = raw.split()
                n = len(p) - 1
                if n < 3:
                    continue

                nv = len(vertex_strings)
                nt = len(texture_strings)
                vi = [0] * n
                ti = [0] * n
                has_tex = True
                for k in range(n):
                    s = p[k + 1].split("/", 2)
                    j = int(s[0])
                    vi[k] = j - 1 if j > 0 else nv + j
                    if len(s) > 1 and s[1]:
                        j = int(s[1])
                        ti[k] = j - 1 if j > 0 else nt + j
                    else:
                        has_tex = False

                v0 = vertex_strings[vi[0]]
                t0 = texture_strings[ti[0]] if has_tex else None
                for i in range(1, n - 1):
                    v_emit(v0)
                    v_emit(vertex_strings[vi[i]])
                    v_emit(vertex_strings[vi[i + 1]])
                    if has_tex:
                        t_emit(t0)
                        t_emit(texture_strings[ti[i]])
                        t_emit(texture_strings[ti[i + 1]])
                    triangle_count += 1

    with open(vertex_out_path, "w") as out:
        out.write("".join(v_out))
    with open(texture_out_path, "w") as out:
        out.write("".join(t_out))

    print(f"Total vertices: {triangle_count * 3}")
    print(f"Total texture cordinates: {triangle_count * 2}")

    return triangle_count


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="objParser",
        description="Parse a Wavefront .obj file into glDrawArrays-ready "
                    "vertex and texture coordinate streams.",
    )
    ap.add_argument("input", nargs="?", default="pear.obj",
                    help="Input OBJ file (default: pear.obj).")
    ap.add_argument("vertex_out", nargs="?", default="finalVertex.txt",
                    help="Vertex coordinate output (default: finalVertex.txt).")
    ap.add_argument("texture_out", nargs="?", default="finalTexture.txt",
                    help="Texture coordinate output (default: finalTexture.txt).")
    args = ap.parse_args(argv)
    parse_obj(args.input, args.vertex_out, args.texture_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
