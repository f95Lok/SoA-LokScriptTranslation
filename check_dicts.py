import io
import re

_variables_ = "variables"
_arguments_ = "arguments"


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
        _variables_: {},
        _arguments_: {},
    }

    variables_entries = xml_to_dict(io.open("xml/variables.xml", 'r', encoding="utf-8"))
    for entry in variables_entries:
        xml_dict[_variables_][entry[0]] = entry[1]

    arguments_entries = xml_to_dict(io.open("xml/arguments.xml", 'r', encoding="utf-8"))
    for entry in arguments_entries:
        xml_dict[_arguments_][entry[0]] = entry[1]

    return xml_dict


xml = read_xml_files()
values = {
        _variables_: {},
        _arguments_: {},
    }

for original, variable in xml[_variables_].items():
    if variable not in values[_variables_]:
        values[_variables_][variable] = []

    if original.lower() not in values[_variables_][variable]:
        values[_variables_][variable].append(original.lower())

for variable in values[_variables_]:
    if len(values[_variables_][variable]) > 1:
        print(variable, values[_variables_][variable], sep="; ")

print("===========================================")

for original, argument in xml[_arguments_].items():
    if argument not in values[_arguments_]:
        values[_arguments_][argument] = []

    if original.lower() not in values[_arguments_][argument]:
        values[_arguments_][argument].append(original.lower())

for argument in values[_arguments_]:
    if len(values[_arguments_][argument]) > 1:
        print(argument, values[_arguments_][argument], sep="; ")
