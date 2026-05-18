# OBJ-Parser

> Fast, forgiving Wavefront `.obj` parser. Streams a model in a single
> pass and emits ready-to-upload vertex and texture coordinate streams
> for OpenGL's `glDrawArrays`.

[![CI](https://github.com/kohterai/OBJ-Parser/actions/workflows/ci.yml/badge.svg)](https://github.com/kohterai/OBJ-Parser/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## What it does

Given an `.obj` file the parser looks at `v` (vertex), `vt` (vertex
texture), and `f` (face) lines. Polygonal faces are triangulated and the
per-vertex coordinates are written out as plain text, formatted to drop
straight into a `glDrawArrays` call:

- `finalVertex.txt` — each float suffixed with `f*x, `
- `finalTexture.txt` — each float suffixed with `f, `

A quad is split into two triangles `(0, 1, 2)` and `(0, 2, 3)`; n-gons
are fan-triangulated around the first vertex.

## Quickstart

```bash
# Run against the default `pear.obj` in the current directory:
python objParser.py

# Or point it at any .obj file:
python objParser.py samples/cube.obj
```

Custom output paths (positional, in order):

```bash
python objParser.py model.obj vertices.txt textures.txt
```

For input like:

```
v -0.257682 -1.674006 0.731635
v -0.132727 -1.662367 0.777859
v -0.467796 -1.580605 0.795138

vt 0.336677 0.109069
vt 0.323670 0.086280
vt 0.333450 0.154337

f 1/1/1 5/2/2 6/3/3 2/4/4
f 2/4/4 6/3/3 2/5/5 1/6/6
f 5/2/2 6/7/7 4/8/8 6/3/3
```

it writes coordinates ready to paste straight into a vertex array:

```
-0.257682f*x, -1.674006f*x, 0.731635f*x, ...
```

and prints:

```
Total vertices: 18
Total texture cordinates: 12
```

## Install

```bash
pip install -e .
# CLI is now on $PATH:
obj-parser samples/cube.obj
```

Or just copy `objParser.py` into your project — it has zero runtime
dependencies.

## Library usage

```python
import objParser

triangles = objParser.parse_obj(
    "model.obj",
    "vertices.txt",
    "textures.txt",
)
print(f"Parsed {triangles} triangles.")
```

## What's supported

| Face type / quirk                            | Status                    |
| -------------------------------------------- | ------------------------- |
| Triangles `f a b c`                          | supported                 |
| Quads `f a b c d`                            | supported                 |
| N-gons (5+ vertices)                         | supported, fan-triangulated |
| `v/vt/vn` tokens                             | supported                 |
| `v//vn` tokens (no texture index)            | supported                 |
| Negative (relative) indices                  | supported                 |
| Comments (`# ...`) and blank lines           | ignored                   |
| `vn`, `vp`, `o`, `g`, `s`, `usemtl`, `mtllib` | ignored                   |

The output format and stdout messages are unchanged from the original
implementation, so existing pipelines and shaders keep working.

## Performance

Roughly **4x faster** than the original on a synthetic 150 000-line OBJ
(50 000 vertices, 50 000 quad faces, 4.7 MB), measured on CPython 3.11:

| Implementation | Best of 5 | Throughput |
| -------------- | --------: | ---------: |
| Original       |    744 ms |   6.3 MB/s |
| Cracked        |    194 ms |  24.2 MB/s |

Reproduce with:

```bash
python bench.py --vertices 50000 --faces 50000 --repeat 5
```

## How it's "cracked"

- **Pre-formatted coordinates.** Each `v` / `vt` line is converted to
  its final output substring (`"x f*x, y f*x, z f*x, "`) on first read,
  so the face loop is just index lookups and append.
- **Single write per file.** Output is collected into a list and emitted
  with one `str.join` + one `write()`, instead of one `write()` per
  float.
- **Single-pass streaming.** No intermediate `finalVertexList` /
  `finalTextureList` data structures — the output is built as faces are
  read.
- **Robust face handling.** Triangles, quads, and n-gons all go through
  the same fan-triangulation code path; `v//vn` and negative indices are
  handled correctly.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

The suite covers triangle / quad / n-gon triangulation, the legacy
byte-exact output format, `v//vn` tokens, negative indices, comments,
and the stdout summary.

## License

[MIT](LICENSE)
