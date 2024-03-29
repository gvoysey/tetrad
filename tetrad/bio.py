"""Cost and Gain functions to evaluate off-target effects and on-target efficacy"""
import numpy as np
import pandas as pd
import json
from tetrad.base import data_path
import os

#  The receptor matrix is derived from Perna et. al (2017) http://dx.doi.org/10.1016/j.ccell.2017.09.004, figure 2b.
receptor_matrix = np.array([
[2, 1, 1, 2, 1, 1, 2, 1, 2, 1, 2, 2, 0, 1, 2, 2, 1, 2, 1, 2, 1, 2, 1, 2, 0, 2, 2, 1, 2, 2, 2, 2, 1, 1, 2, 0, 2, 1, 2, 2, 0, 3, 1],
[0, 1, 1, 1, 1, 0, 1, 2, 2, 0, 2, 2, 1, 1, 2, 2, 0, 1, 0, 1, 0, 2, 2, 1, 1, 1, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 2, 2, 0, 3, 2],
[0, 2, 1, 2, 2, 1, 2, 1, 1, 1, 1, 2, 2, 1, 0, 2, 2, 2, 1, 0, 1, 2, 2, 0, 0, 2, 2, 1, 2, 0, 2, 0, 0, 2, 0, 0, 1, 2, 2, 2, 0, 1, 1],
[0, 1, 1, 2, 1, 1, 2, 2, 2, 1, 1, 2, 1, 1, 1, 2, 2, 1, 2, 1, 0, 1, 1, 2, 0, 0, 1, 1, 2, 1, 2, 0, 0, 0, 0, 0, 2, 1, 1, 1, 0, 1, 0],
[0, 0, 2, 1, 2, 2, 2, 1, 2, 0, 1, 0, 2, 2, 1, 2, 0, 2, 0, 0, 0, 2, 2, 2, 0, 1, 1, 2, 2, 1, 2, 0, 2, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0],
[0, 2, 1, 2, 1, 0, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 2, 1, 1, 1, 1, 0, 1],
[0, 0, 1, 2, 0, 1, 2, 0, 0, 2, 2, 2, 0, 2, 2, 1, 0, 1, 0, 1, 1, 0, 2, 1, 0, 1, 0, 0, 0, 2, 2, 0, 2, 1, 1, 0, 2, 0, 2, 1, 0, 2, 1],
[0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 2, 1],
[0, 0, 2, 0, 0, 0, 0, 1, 2, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 2, 1],
[0, 0, 1, 0, 4, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 4, 0, 4, 4, 0, 0, 4, 2, 0, 0, 4, 4, 0, 0, 2, 4, 0, 0, 0, 0, 1, 0, 0, 0, 4, 3, 1],
[0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 2, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0],
[0, 0, 0, 0, 4, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 4, 0, 4, 4, 0, 0, 4, 0, 0, 0, 4, 4, 0, 0, 1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 4, 2, 0],
[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 2],
[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1, 3],
[0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 4, 4, 0, 0, 4, 0, 0, 0, 4, 4, 1, 0, 0, 4, 0, 0, 1, 0, 0, 0, 0, 0, 4, 2, 0],
[0, 0, 0, 0, 4, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 4, 0, 4, 4, 0, 0, 4, 0, 0, 0, 4, 4, 0, 0, 1, 4, 0, 0, 0, 0, 1, 0, 0, 0, 4, 2, 0],
[0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1],
[0, 0, 1, 0, 4, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 4, 0, 4, 4, 1, 0, 4, 0, 0, 0, 4, 4, 1, 0, 0, 4, 0, 0, 0, 0, 1, 0, 0, 0, 4, 2, 0],
[0, 0, 0, 0, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 4, 4, 0, 0, 4, 0, 0, 0, 4, 4, 1, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 4, 2, 0],
[0, 0, 0, 0, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 4, 4, 0, 0, 4, 0, 0, 0, 4, 4, 1, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 4, 2, 1],
[0, 0, 0, 0, 4, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 0, 0, 4, 0, 0, 0, 4, 4, 0, 0, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 4, 1, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 4, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 4, 4, 0, 0, 4, 0, 0, 0, 4, 4, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1, 0],
[0, 0, 0, 0, 4, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 4, 4, 0, 0, 4, 0, 0, 0, 4, 4, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1, 0],
[2, 1, 3, 3, 3, 2, 3, 3, 0, 3, 3, 3, 3, 3, 3, 1, 0, 3, 0, 1, 3, 2, 3, 3, 0, 3, 2, 1, 2, 3, 2, 0, 3, 2, 3, 3, 1, 3, 3, 3, 3, 3, 3],
[0, 2, 2, 2, 3, 0, 3, 2, 2, 3, 2, 2, 3, 2, 2, 3, 2, 2, 2, 2, 0, 3, 3, 3, 0, 3, 2, 2, 2, 2, 1, 2, 2, 1, 2, 0, 2, 2, 2, 2, 2, 0, 2],
[0, 2, 1, 0, 4, 0, 2, 1, 0, 1, 1, 2, 0, 2, 2, 2, 4, 0, 4, 4, 1, 1, 4, 0, 0, 1, 4, 4, 2, 0, 2, 4, 1, 1, 0, 1, 2, 0, 1, 2, 4, 0, 0],
[1, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0, 2, 0, 2, 0, 1, 0, 0, 0, 0, 1, 2, 2, 0, 0, 1, 0, 0, 0, 3, 2, 0, 2, 2, 1, 0, 1, 0, 3, 0, 0, 2, 2],
[0, 0, 2, 1, 1, 0, 3, 1, 1, 0, 0, 1, 0, 1, 1, 2, 1, 1, 1, 1, 0, 2, 2, 1, 0, 1, 1, 1, 2, 0, 0, 1, 0, 1, 1, 0, 2, 1, 1, 1, 0, 0, 0],
[0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 2, 0, 0, 2, 0, 3, 0, 0, 0, 2, 0, 0, 2, 2],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 2, 3],
])

SURFACE_TARGETS = '''ITGB5 PTPRJ SLC30A1 EMC10 SLC6A6 TNFRSF1B CD82 ITGAX CR1 DAGLB SEMA4A TLR2 LTB4R P2RY13 LILRB2 EMB 
CD96 LILRB3 LILRA6 LILRA2 EMR2 LILRB4 CD70 CCR1 CD44 IL3RA FOLR2 CD38 FUT3 CD33 CLEC12A'''.split()

tissue_types = '''adipose_tissue adrenal bladder brain bronchus eye gut heart kidney esophagus liver lung nasopharynx 
oropharynx pancreas rectum skeletal_muscle skin smooth_muscle soft_tissue spinal_cord stomach appendix breast
cerumen cervix epididymis fallopian_tube gallbladder lymph_node ovary parathyroid prostate seminal
spleen synovial_fluid testis thyroid tonsil uterus vagina blood bone'''.split()

df = pd.DataFrame(data=receptor_matrix.T, index=tissue_types, columns=SURFACE_TARGETS)

weights = np.array([3, 2, 2, 3, 3, 2, 2, 3, 3, 2, 3, 3, 2, 2, 3, 2, 3, 1, 3, 3, 3, 2, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1,
                    1, 1, 2, 1, 1, 1, 1, 1, 3, 3]) / 3


def cost(dyad):
    """Returns the cost function for the given pair of targets.  The cost function is
    a measure of predicted selectivity for AML-specific cell types"""
    dyad = list(dyad)
    a = df[dyad[0]]
    b = df[dyad[1]]
    retval = []
    for i, (aa, bb) in enumerate(zip(a, b)):
        retval.append((aa ** 2 + bb ** 2) * weights[i])
    return np.mean(retval)


gene_data = os.path.join(data_path, 'bloodspot_figure_2.json')
with open(gene_data, 'r') as f:
    antigens = json.load(f)
    antigens.pop('date_accessed')


def gain(tetrad):
    """Return the gain function of a pair of targets.
    The gain function is a measure of predicted efficacy against known AML cell types."""
    return sum(dyad_gain(d.name) for d in tetrad)


def dyad_gain(dyad):
    for gene_id in dyad:
        # bloodspot data is now a dict.  each key is one column in the bloodspot data plot, each value is every data point for that column.
        bloodspot_data = antigens[gene_id]
        # tbd here
    return 0  # for now; return real gain later.


if __name__ == "__main__":
    print(cost(('CD96', 'CD33')))
