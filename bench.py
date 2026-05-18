"""Synthetic benchmark for objParser.

Generates a random OBJ of configurable size, parses it, and prints wall
clock time plus throughput. Useful for sanity-checking performance
regressions.

Run with: ``python bench.py [--vertices N] [--faces N] [--repeat N]``
"""

from __future__ import annotations

import argparse
import contextlib
import os
import random
import tempfile
import time
from pathlib import Path
from statistics import median

import objParser


def write_synthetic_obj(path: Path, n_vertices: int, n_faces: int, seed: int = 0) -> None:
    rng = random.Random(seed)
    with path.open("w") as f:
        for _ in range(n_vertices):
            f.write(f"v {rng.random():.6f} {rng.random():.6f} {rng.random():.6f}\n")
        for _ in range(n_vertices):
            f.write(f"vt {rng.random():.6f} {rng.random():.6f}\n")
        for _ in range(n_faces):
            a, b, c, d = rng.sample(range(1, n_vertices + 1), 4)
            f.write(f"f {a}/{a} {b}/{b} {c}/{c} {d}/{d}\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--vertices", type=int, default=50_000)
    ap.add_argument("--faces", type=int, default=50_000)
    ap.add_argument("--repeat", type=int, default=3, help="Number of timing runs.")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        obj = d / "bench.obj"
        v_out = d / "v.txt"
        t_out = d / "t.txt"

        write_synthetic_obj(obj, args.vertices, args.faces)
        size_mb = obj.stat().st_size / (1024 * 1024)
        print(f"Synthetic OBJ: {args.vertices} verts, {args.faces} faces "
              f"({size_mb:.1f} MB on disk)")

        runs = []
        tris = 0
        with open(os.devnull, "w") as devnull:
            for i in range(args.repeat):
                start = time.perf_counter()
                with contextlib.redirect_stdout(devnull):
                    tris = objParser.parse_obj(obj, v_out, t_out)
                runs.append(time.perf_counter() - start)
                print(f"  run {i + 1}: {runs[-1] * 1000:7.1f} ms")

    best = min(runs)
    med = median(runs)
    print(f"\n{tris} triangles output")
    print(f"best   {best * 1000:7.1f} ms   ({size_mb / best:6.1f} MB/s)")
    print(f"median {med * 1000:7.1f} ms   ({size_mb / med:6.1f} MB/s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
