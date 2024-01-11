import io
import re

_text_ = "text"


def xml_to_dict(file):
    entries = []
    for line in file.readlines():
        if "entry" in line:
            original = re.search(r'(?<=original=")[^"]*(?=")', line).group(0).replace("&amp;", "&").replace("&quot;", '"')
            translated = re.search(r'(?<=translated=")[^"]*(?=")', line).group(0).replace("&amp;", "&")
            entries.append((original, translated))

    return entries


def read_xml_files():
    xml_dict = {
        _text_: {},
    }

    variables_entries = xml_to_dict(io.open("xml/text.xml", 'r', encoding="utf-8"))
    for entry in variables_entries:
        xml_dict[_text_][entry[0]] = entry[1]

    return xml_dict


def write_xml(data_type):
    global xml

    xml_file = io.open("xml/"+data_type+".xml", 'w', encoding="utf-8")
    xml_file.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
    xml_file.write('<dictionary>\n')
    for original, translated in xml[data_type].items():
        xml_file.write("\t<entry original=\"" + original.replace("&", "&amp;").replace('"', "&quot;") + "\" translated=\"" + translated.replace("&", "&amp;") + "\"/>\n")

    xml_file.write('</dictionary>')


xml = read_xml_files()
values = {
        _text_: {},
    }

target = "''"
replacement = "&#39;"
for ori, tran in xml[_text_].items():
    if target in tran:
        xml[_text_][ori] = tran.replace(target, replacement)

write_xml(_text_)
