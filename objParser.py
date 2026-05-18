"""Cracked OBJ parser.

Reads an OBJ file and writes vertex / texture coordinate streams suitable
for ``glDrawArrays``.  Default input path, output paths and output text
format match the original implementation byte-for-byte:

- ``finalVertex.txt``: each float suffixed with ``f*x, ``
- ``finalTexture.txt``: each float suffixed with ``f, ``
- stdout: ``Total vertices: N`` and ``Total texture cordinates: M``

Compared with the original this version:

- Streams the input in a single pass and pre-formats each ``v`` / ``vt``
  on read, so triangulation is just index lookups + a final ``join``.
- Buffers the output and emits each file with a single ``write``.
- Fan-triangulates faces of any size (the original handled quads only).
- Tolerates ``v//vn`` tokens (missing texture index), trailing
  whitespace, comments, and OBJ-spec negative (relative) indices.
"""

import sys


def parse_obj(input_path='pear.obj',
              vertex_out_path='finalVertex.txt',
              texture_out_path='finalTexture.txt'):
    vertex_strings = []
    texture_strings = []
    v_store = vertex_strings.append
    t_store = texture_strings.append

    v_out = []
    t_out = []
    v_emit = v_out.append
    t_emit = t_out.append

    triangle_count = 0

    with open(input_path, 'r') as src:
        for raw in src:
            if raw.startswith('v '):
                p = raw.split()
                v_store(f'{p[1]}f*x, {p[2]}f*x, {p[3]}f*x, ')
            elif raw.startswith('vt '):
                p = raw.split()
                t_store(f'{p[1]}f, {p[2]}f, ')
            elif raw.startswith('f '):
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
                    s = p[k + 1].split('/', 2)
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

    with open(vertex_out_path, 'w') as out:
        out.write(''.join(v_out))
    with open(texture_out_path, 'w') as out:
        out.write(''.join(t_out))

    print(f'Total vertices: {triangle_count * 3}')
    print(f'Total texture cordinates: {triangle_count * 2}')


if __name__ == '__main__':
    parse_obj(*sys.argv[1:])
