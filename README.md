.OBJ-Parser
==========

OBJ file parser written in Python.  Converts OBJ files to vector and texture coordinates to plot in OpenGL with glDrawArrays.

<h2>Example .obj file format</h2>
The Parser currently only examines lines that begin with "v" (vertex), "vt" (vertex texture), and "f" (faces).
Furthermore the faces should consist of the standard .obj format of v/vt/n/... where the values are separated by slashes.

v -0.257682 -1.674006 0.731635
v -0.132727 -1.662367 0.777859
v -0.467796 -1.580605 0.795138

vt 0.336677 0.109069
vt 0.323670 0.086280
vt 0.333450 0.154337

f 1/1/1 5/2/2 6/3/3 2/4/4
f 2/4/4 6/3/3 2/5/5 1/6/6
f 5/2/2 6/7/7 4/8/8 6/3/3

The code is currently optimized for quaderateral faces.  Given faces f=[0, 1, 2, 3] the parser will return appropiate vertex and texture coordinates for the two triangles [0, 1, 2] and [0, 2, 3].

<h2>Output</h2>
Two files are produced.  The first file conists of the vertex coordinates and the second file the texture coordinates.
The terminal prints the total number of vertices for explicitly allocating array memory.