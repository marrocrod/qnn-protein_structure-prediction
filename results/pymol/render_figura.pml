# PyMOL scene used for the reconstruction figure.
# Usage: copy next to the exported PDBs (results/pymol/pdb/), set PID and run `pymol render_figura.pml`.
# Colours: true structure = cyan, MDS = orange, refined = green.

python
PID = "20#2KJI_1_A"          # protein id as written by Bloque 18 of the notebook
cmd.reinitialize()
cmd.load(f"{PID}_real.pdb", "real")
cmd.load(f"{PID}_mds.pdb", "mds")
cmd.load(f"{PID}_refined.pdb", "refined")
python end

hide everything
set cartoon_trace_atoms, 1
show cartoon
cartoon tube
set cartoon_tube_radius, 0.6
color cyan,   real
color orange, mds
color green,  refined
bg_color white
set ray_opaque_background, 1
orient
ray 2400, 1800
python
cmd.png(f"{PID}_figura.png", dpi=300)
python end
