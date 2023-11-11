#!/usr/bin/env python3
# usage: txtsplit.py <input_file_name> <output_dir>
# splits a txt2gam file into individual location files
# encoded in utf-8, for git to better handle
# Original file from girllife-ecv. https://git.tfgamessite.com/KevinSmarts/girllife-ecv

import os
import sys
import re
import io
import xml.etree.ElementTree as ET

assert len(sys.argv) == 3, "usage:\ntxtsplit.py <input_file_name> <output_dir>"
iname = str(sys.argv[1])
odir = str(sys.argv[2])

# read the project xml file first
# let's do this later in order to implement directory structure
ifile = io.open(iname, 'r', encoding='utf-16')

location_dict = {}
for line in ifile:
    if line[0] == "#":
        location = line[2:]
        location = location.strip("\n")
        location_dict[location] = []
        location_dict[location].append(line)
    else:
        location_dict[location].append(line)

for key, lines in location_dict.items():
    oname = os.path.join(odir, key + '.qsrc' )
    ofile = io.open(oname, 'w', encoding='utf-8')
    for line in lines:
        ofile.write(line)
    ofile.close()

