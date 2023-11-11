#!/usr/bin/env python3
# usage: txtmerge.py <input_dir> <output_file_name>
# does the exact opposite of txtsplit.py
# Original file from Girl Life ecv - Betmonty

import os
import sys
import re
import io
import xml.etree.ElementTree as ET
from xml.dom import minidom
def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, encoding='utf-8', method='xml')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

assert len(sys.argv) == 3, "usage:\nqprojgen.py <input_dir> <output_file_name>"
idir = str(sys.argv[1])
oname = str(sys.argv[2])
ofile = io.open(oname, 'w', encoding='utf-8', newline='\r\n')
locations = os.listdir(path=idir)
locations = [location[:-5] for location in locations]
first_loc = locations.index("star")
root = ET.Element("QGen-project", attrib={"version": "4.0.0 beta 1"})
location_holder = ET.SubElement(root, 'Structure')
ET.SubElement(location_holder, "Location", attrib={"name": locations[first_loc]})
locations.pop(first_loc)
for location in locations:
    ET.SubElement(location_holder, "Location", attrib={"name": location})
xml_file = prettify(root)
ofile.write(xml_file)
ofile.close()
