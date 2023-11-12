# Hello there! (General Kenobi). If you're reading this then you've really gone off the deep end.
# To quote a meme: "When I wrote this script, only me and God knew how it works. Now, only God knows."
# In all seriousness, this was made as an alternative to QSPTools specifically for the game "Son of Asia"
# I advise against trying to use or adapt this script for another game. While I tried to keep it general at the start,
#   I did not succeed, and there are many matches and finds that I doubt will be present in other games.
# My attempts at making general cases also dwindled as my frustration grew.
# It is a series of regex splits and finds to attempt to get all Chinese text that does not reference a filename
#   while also categorizing it into variables, locations, arguments and plain text.
#   It also checks all filename references around the code and reverts all translation for embedded variables
#   It also creates auxiliary variables for embedded "ARGS" / "args" filename references
#       This might result in useless arguments in some places but who cares as long as it doesn't break anything.
# For now, because no translator API I was able to find was truly free, the script works based on detecting clipboard
#   changes. You will be prompted to translate a text, which will also be automagically added to your clipboard.
#   When you copy something else into your clipboard, the script will automagically use that as the translation.
#   So be careful how you CTRL+C around your code. If you fuck up, you can just stop the execution and edit in the xml.
# If you're reading this paragraph, it means I still didn't find a free API.
#   If you know of one, or one that allows scraping without any consequences, please do let me know.
#   There is an auto function now, but it's based on being able to alt tab into yandex and using the keyboard shortcuts.
#   It's very fragile. Use it at your own discretion
# This script also requires an editor that has a console capable of handling UTF-8 prints.
#   I used PyCharm. Sublime doesn't work. Plain old console kinda works, but you won't see the text you're translating
#   VSCode idk, I don't use VSCode. I hate it.
# Other than that, it needs 'pyperclip'.
# It is 5:34 AM for me. I'm going to sleep
# Have fun :D

import pyperclip as clip
import pyautogui as pgui
import random
import time
import io
import re
import os


_variables_ = "variables"
_locations_ = "locations"
_arguments_ = "arguments"
_text_ = "text"

_translations_ = []

_use_auto_translate_ = True
_alt_tabbed_ = False

_print_output_ = True
_use_old_dict_ = False
_update_xml_ = True

_in_partial_hyperlink_ = False
_current_location_ = ""

regex_main = r"\s*\S+\s*(?:=|\+=|-=|\*=|/=)\s*.+$|if [^:]+:|<div.+</div>|<div.+$|<a.+</a>|(?:<p>|<p).+</p>|<p>.+$|<font.+</font>|<font[^']+(?=')|<span.[^']+(?=')|(?:gs|gt|dynamic|KILLVAR|killvar).+$|#\s.+$|\-{3}\s[^-]+\s\-+"

regex_extract_from_string = r"(?<='')[^']+(?='')|(?<=\"\")[^\"]+(?=\"\")|(?<=')[^']+(?=')|(?<=\")[^\"]+(?=\")"
regex_extract_from_string_partial_no_end = r"(?:^\s*|=\s*)\"[^\"]+$|(?:^\s*|=\s*)'[^']+$"
regex_extract_from_string_partial_no_beg = r"^\s*[^\"]+\"$|^\s*[^']+'$"

regex_extract_rand_func = r"(?:(?<=[ \[\-+*\/=])|^)(?:rand|RAND)\([^\)]+\)(?:(?=[ \]\-+*\/])|$)"
regex_extract_strings = r"''[^']+''|'[^']+'|\"\"[^\"]+\"\"|\"[^\"]+\""

regex_everything_mostly = r"[ A-z0-9`~!@#$%^&*()\-_=+\[\]{};'\\:\"|,./<>?]+"

# regex_split_expression_if = r"[^<>!=]+(?=[<>=!])|(?<=[<>=!])[^<>!=]+"
regex_split_if_arguments = r"(?<=[ 0-9\(\)'\"])(?:or|and)(?=[0-9\(\)'\"\$ ])"
regex_split_expression = r"[+\-*\/<>]*=|[!<>]"
regex_split_html_long = r"(?<!<)<(?!<)|(?<!>)>(?!>)"
regex_split_function = r"(?<=[\"'])\s*,\s*(?=[\"'])"

regex_detect_single_string_assignment = r"^\s*[^=+\-*/!<>]+(?:\+=|-=|\*=|/=|<=|>=|=|!|<|>)(?:'(?!')|\"(?!\")).*(?:'(?!')|\"(?!\"))\s*$"
regex_detect_partial_hyperlink = r"href='[^']+$|href=\"[^\"]+$"

regex_embedded_variable = r"<{2}[^<>]+>{2}"
regex_operators = r"[+\-*/&]"

ch_punctuation_marks = ["，", ",", "。", "·", ".", "...", "？", "?", "！", "!", "：", ":", "—", "【", "】"]
match_function = ["gs", "gt", "dynamic", "killvar", "KILLVAR"]
ignore_terms = ["img src", "source src"]
html_tags = ["<div", "<a", "<p", "<font"]

_current_line_ = ""


def old_xml_to_dict(file):
    entries = {}
    for line in file.readlines():
        if "entry" in line:
            original = re.search(r'(?<=original=")[^"]*(?=")', line).group(0)
            translated = re.search(r'(?<=translated=")[^"]*(?=")', line).group(0)
            entries[original] = translated

    return entries


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
        _locations_: {},
        _arguments_: {},
        _text_: {}
    }

    variables_entries = xml_to_dict(io.open("xml/variables.xml", 'r', encoding="utf-8"))
    for entry in variables_entries:
        xml_dict[_variables_][entry[0]] = entry[1]

    locations_entries = xml_to_dict(io.open("xml/locations.xml", 'r', encoding="utf-8"))
    for entry in locations_entries:
        xml_dict[_locations_][entry[0]] = entry[1]

    arguments_entries = xml_to_dict(io.open("xml/arguments.xml", 'r', encoding="utf-8"))
    for entry in arguments_entries:
        xml_dict[_arguments_][entry[0]] = entry[1]

    text_entries = xml_to_dict(io.open("xml/text.xml", 'r', encoding="utf-8"))
    for entry in text_entries:
        xml_dict[_text_][entry[0]] = entry[1]

    return xml_dict


def update_xml(original, translation, data_type):
    xml[data_type][original] = translation

    xml_file = io.open("xml/"+data_type+".xml", 'r', encoding="utf-8")
    xml_lines = xml_file.readlines()
    xml_file.close()

    while xml_lines.pop().strip() != "</dictionary>":
        continue

    xml_lines.append("\t<entry original=\"" + original.replace("&", "&amp;").replace('"', "&quot;") + "\" translated=\"" + translation.replace("&", "&amp;") + "\"/>\n")
    xml_lines.append("</dictionary>")
    xml_file = io.open("xml/"+data_type+".xml", 'w', encoding="utf-8")
    for line in xml_lines:
        xml_file.write(line)


def translate(text, data_type):
    global _alt_tabbed_
    global _current_location_
    print_progress = True
    if text in xml[data_type]:
        _translations_.append((text, xml[data_type][text]))
        if _print_output_:
            print(_current_line_ + " Translated: " + text + " [" + data_type + "] to: " + xml[data_type][text])

        if _current_location_ == "" and data_type == _locations_:
            _current_location_ = xml[data_type][text]
    else:
        if text in old_xml and _use_old_dict_:
            translation = old_xml[text]
        elif data_type == _text_ and text[0] in ["·", ":"] and text[1:].strip() in old_xml and _use_old_dict_:
            translation = text[0] + old_xml[text[1:].strip()]
        else:
            # require manual translation, can't find free API, idk how QSPTools does it.
            if data_type == _variables_ and text[0] == "$":
                compare_text = text[1:]
            else:
                compare_text = text

            clip.copy(compare_text)
            if _print_output_:
                print(_current_line_ + " Provide translation for: " + text + " [" + data_type + "] (Copied to clipboard)")
            print_progress = False
            if _use_auto_translate_:
                if not _alt_tabbed_:
                    pgui.hotkey("alt", "tab")
                    _alt_tabbed_ = True
                pgui.hotkey("alt", "d")
                time.sleep(random.random())
                pgui.hotkey("ctrl", "v")
                time.sleep(random.random())
                i = 0
                while clip.paste() == compare_text:
                    if i > 6:
                        break

                    pgui.hotkey("alt", "c")
                    time.sleep(random.random())
                    i += 1
            else:
                clip.waitForNewPaste()

            translation = clip.paste()

        if data_type != _text_:
            translation = translation.replace(" ", "_").lower()
            while translation.find("__") != -1:
                translation = translation.replace("__", "_")

        translation = translation.replace("'", "`").replace('"', "`")

        if _update_xml_:
            update_xml(text, translation, data_type)

        if _current_location_ == "" and data_type == _locations_:
            _current_location_ = translation

        _translations_.append((text, translation))
        if _print_output_ and print_progress:
            print(_current_line_ + " Translated: " + text + " [" + data_type + "] to: " + translation)


def update_dict(new_data, data_type):
    if type(new_data) != list:
        new_data = [new_data]

    for d in new_data:
        if re.sub(regex_everything_mostly, "", d).strip() != "":
            entry = d.strip()
            translate(entry, data_type)


def extract_from_string(text):
    strings = re.findall(regex_extract_from_string, text)
    if len(strings) > 0:
        return strings

    partial_no_end = re.search(regex_extract_from_string_partial_no_end, text)
    if partial_no_end is not None:
        return [text[1:]]

    partial_no_beg = re.search(regex_extract_from_string_partial_no_beg, text)
    if partial_no_beg is not None:
        return [text[:-1]]

    return []


def handle_array(bracket):
    for brk in re.split(r"[\[\]]", bracket):
        if any(quote in brk for quote in ["'", '"']):
            handle_texts(extract_from_string(brk), force_type=_arguments_)
        else:
            update_dict(brk, _variables_)


def handle_embedded_variable(embedded_variable):
    for variable in re.split(regex_operators, embedded_variable[2:-2]):
        if any(bracket in variable for bracket in ["[", "]"]):
            handle_array(variable)
        else:
            update_dict(variable, _variables_)


def handle_embedded_variables(text):
    for embedded_variable in re.findall(regex_embedded_variable, text):
        handle_embedded_variable(embedded_variable)


def handle_text(text, force_type=_text_):
    embedded_variables = re.findall(regex_embedded_variable, text)
    texts = re.split(regex_embedded_variable, text)

    while len(embedded_variables) > 0 or len(texts) > 0:
        if len(embedded_variables) == 0:
            update_dict(texts.pop(0).replace("</p>", ""), force_type)
        elif len(texts) == 0:
            handle_embedded_variable(embedded_variables.pop(0))
        elif text.find(texts[0]) < text.find(embedded_variables[0]):
            update_dict(texts.pop(0).replace("</p>", ""), force_type)
        else:
            handle_embedded_variable(embedded_variables.pop(0))


def handle_texts(texts, force_type=_text_):
    for text in texts:
        handle_text(text, force_type=force_type)


def handle_expression(expressions, callback=None):
    expressions = re.split(regex_split_expression, expressions, 1)

    for expression in expressions:
        if len(extract_from_string(expression)) == 1:
            if callback == "if":
                force_type = _arguments_
            else:
                force_type = _text_

            if any(tag in expression for tag in html_tags):
                handle_html(extract_from_string(expression)[0])
            else:
                handle_texts(extract_from_string(expression), force_type=force_type)

            continue

        if "rand(" in expression or "RAND(" in expression:
            rand_functions = re.findall(regex_extract_rand_func, expression.strip())
            for rand_function in rand_functions:
                handle_function(rand_function)
                expression = expression.replace(rand_function, "", 1)

        expr_sides = re.split(regex_operators, expression)

        for expr_side in expr_sides:
            if any(bracket in expr_side for bracket in ["[", "]"]):
                handle_array(expr_side)
            elif any(quote in expr_side for quote in ["'", '"']):
                if callback == "if":
                    handle_texts(extract_from_string(expr_side), force_type=_arguments_)
                else:
                    handle_texts(extract_from_string(expr_side))
            else:
                update_dict(re.sub(r"[()]", "", expr_side), _variables_)


def handle_location(location):
    location = re.sub("[#\-]+", "", location)
    update_dict(location, _locations_)


def handle_function(function):
    if "gt" in function or "gs" in function:
        if "gt" in function:
            function = function[function.find("gt")+2:].strip()
        elif "gs" in function:
            function = function[function.find("gs")+2:].strip()

        if "," in function:
            function = re.split(regex_split_function, function)

            for i in range(len(function)):
                if i == 0:
                    handle_texts(extract_from_string(function[i]), force_type=_locations_)
                else:
                    if any(ch_punctuation in function[i] for ch_punctuation in ch_punctuation_marks) or i > 1 and "_" not in function[i] and len(re.sub(r"[\"'<>]", "", function[i])) >= 10:
                        handle_texts(extract_from_string(function[i]))
                    else:
                        handle_texts(extract_from_string(function[i]), force_type=_arguments_)

        else:
            handle_texts(extract_from_string(function), force_type=_locations_)

    elif "KILLVAR" in function or "killvar" in function:
        if "KILLVAR" in function:
            function = function[function.find("KILLVAR") + 7:].strip()
        elif "killvar" in function:
            function = function[function.find("killvar") + 7:].strip()

        if "," in function:
            function = function[:function.find(",")].strip()

        function = function[1:-1]

        update_dict(function, _variables_)

    elif "rand" in function or "RAND" in function:
        function = re.split(r"[(),]|"+regex_operators, function)
        for arg in function:
            if any(quote in arg for quote in ["'", '"']):
                handle_texts(extract_from_string(arg))
            else:
                update_dict(arg, _variables_)


def handle_if_arguments(if_matches):
    if_matches = re.split(regex_split_if_arguments, if_matches)

    for if_match in if_matches:
        expression = re.sub("if|:", "", if_match)
        if "ARGS" in expression or "args" in expression:
            handle_expression(expression, callback="if")
        else:
            handle_expression(expression)


def handle_div(div):
    for text in extract_from_string(div):
        handle_text(text)


def reconstruct_exec(expressions):
    i = 0
    while i < len(expressions)-1:
        part_1 = re.search(r"'[^']+$|\"[^\" ]+$", expressions[i].strip())
        part_2 = re.search(r"^[^']+'|^[^\" ]+\"", expressions[i+1].strip())
        if part_1 is not None and part_2 is not None:
            expressions[i] += "&" + expressions[i+1]
            expressions.pop(i+1)
        else:
            i += 1

    return expressions


def handle_exec(statement):
    expressions = re.split("&", statement[statement.find("exec:") + 5:])

    if len(expressions) > 1:
        expressions = reconstruct_exec(expressions)

    for expression in expressions:
        if any(function in expression for function in match_function):
            handle_function(expression)

        else:
            handle_expression(expression)


def this_fucking_dev_man_2(hyperlink):
    hyperlink = re.sub(r'"\s*"', '" ', hyperlink)
    return hyperlink


def handle_partial_hyperlink(hyperlink, state):
    hyperlink = hyperlink.strip()
    if state == "beg":
        if hyperlink[-1] == "&":
            hyperlink = hyperlink[:-1]
        hyperlink += '"'

        return hyperlink

    elif state == "mid":
        hyperlink = '"exec:' + hyperlink
        if hyperlink[-1] == "&":
            hyperlink = hyperlink[:-1]
        hyperlink += '"'
        return hyperlink

    elif state == "end":
        hyperlink = '<a href="exec:' + hyperlink
        handle_html(hyperlink)


def handle_hyperlink(hyperlink):
    global _in_partial_hyperlink_
    if not _in_partial_hyperlink_ and re.search(regex_detect_partial_hyperlink, hyperlink) is not None:
        _in_partial_hyperlink_ = True
        hyperlink = handle_partial_hyperlink(hyperlink, state="beg")
        statements = re.findall(regex_extract_strings, hyperlink)
    elif _in_partial_hyperlink_:
        if "</a>" not in hyperlink:
            hyperlink = handle_partial_hyperlink(hyperlink, state="mid")
            statements = [hyperlink]
        else:
            _in_partial_hyperlink_ = False
            handle_partial_hyperlink(hyperlink, state="end")
            return
    else:
        if re.search(r'"\s*"\s*\w', hyperlink) is not None:
            hyperlink = this_fucking_dev_man_2(hyperlink)

        statements = re.findall(regex_extract_strings, hyperlink)

    for statement in statements:
        if "exec" in statement:
            handle_exec(statement[1:-1])

        else:
            handle_div(statement)


def reconstruct_html(tags):
    i = tags.index("br")
    while i != -1:
        if i+1 >= len(tags) or i-1 <= 0:
            tags.pop(i)
        else:
            tags[i-1] += "<br>" + tags[i+1]
            tags.pop(i+1)
            tags.pop(i)

        try:
            i = tags.index("br")
        except ValueError:
            break

    return tags


def this_fucking_dev_man(html, opener_symbol, max_opener, closer_symbol, max_closer):
    count = 0
    i = 0
    while i < len(html):
        if "</$LB" in html:
            return html

        if html[i] == opener_symbol:
            count += 1
        elif html[i] == closer_symbol:
            count -= 1

        if count == max_opener:
            html = html[:i] + html[i + 1:]
            count -= 1
        elif count == max_closer:
            html = html[:i] + html[i + 1:]
            count += 1
        else:
            i += 1

    return html


def handle_html(html):
    if html.count("<") != html.count(">"):
        html = this_fucking_dev_man(html, "<", 3, ">", -1)

    if "<p>" in html and html[-1] == "'":
        html = html[:-1]
    html = re.split(regex_split_html_long, html)

    if len(html) > 2 and "br" in html:
        html = reconstruct_html(html)

    for tag in html:
        if "img " in tag or "source " in tag:
            handle_embedded_variables(tag)

        elif "<div " in tag or re.match("^div ", tag) or "<span " in tag or re.match("^span ", tag):
            handle_div(tag)

        elif "<a " in tag or re.match("^a ", tag):
            handle_hyperlink(tag)

        else:
            handle_text(tag)


def analyze_expression(match):
    if "&" in match or "else:" in match:
        expressions = re.split(r"&|else:", match)
        for expression in expressions:
            expression = expression.strip()
            if any(function in expression for function in match_function):
                handle_function(expression)
            elif len(extract_from_string(expression)) == 1 and expression[0] == expression[-1]:
                if any(tag in expression for tag in html_tags):
                    handle_html(extract_from_string(expression)[0])
                else:
                    handle_texts(extract_from_string(expression))
            else:
                handle_expression(expression)
    else:
        handle_expression(match)


def get_data(filepath):
    global _current_line_
    global _current_location_
    _current_location_ = ""
    file = io.open("files/"+filepath, 'r', encoding="utf-8")
    new_file = []
    lines = file.readlines()
    for i, line in zip(range(len(lines)), lines):
        _current_line_ = "[" + filepath + "] (" + str(i + 1) + "/" + str(len(lines)) + ")"\

        if i == 95:
            print("debug")

        if re.sub(regex_everything_mostly, "", line).strip() == "":
            new_file.append(line)
            continue

        if line.strip()[0] == "!":
            new_file.append(line)
            continue

        if any(ignore in line for ignore in ignore_terms):
            handle_embedded_variables(line)

        elif _in_partial_hyperlink_:
            handle_hyperlink(line.strip())

        else:
            matches = re.findall(regex_main, line)
            if len(matches) > 0:
                for match in matches:
                    if re.search("if\s[^:]+:", match) is not None:
                        handle_if_arguments(match)

                    elif re.search(r"^\s*[^=<]+=", match) is not None:
                        analyze_expression(match)

                    elif any(tag in match for tag in html_tags):
                        handle_html(match)

                    elif any(function in match for function in match_function):
                        handle_function(match)

                    elif re.search("^#", match) is not None or re.search(r"^---\s.+\s-+", match) is not None:
                        handle_location(match)

                    else:
                        analyze_expression(match)
            else:
                handle_texts(extract_from_string(line.strip()))

        new_line = line
        for _translation_ in _translations_:
            new_line = new_line.replace(_translation_[0], _translation_[1], 1)
        new_file.append(new_line)

        _translations_.clear()

    file.close()
    if filepath[:-5] in xml[_locations_]:
        file = io.open("translated/"+xml[_locations_][filepath[:-5]]+".qsrc", 'w', encoding="utf-8")
    else:
        file = io.open("translated/"+filepath, 'w', encoding="utf-8")

    for line_n in new_file:
        file.write(line_n)
    file.close()


def find_key_by_value(value, data_type):
    if value in xml[data_type].values():
        original = ""
        for ch, en in xml[data_type].items():
            if value == en:
                original = ch
                break
        return original
    else:
        return value


def correct_translations():
    regex_find_embedded_filenames = r"(?<=images)[/\\].*<<[^>]+>>"
    regex_find_variable_assignment_beg = r"(?:^|(?<=\s|:|&))"
    regex_find_variable_assignment_end = r"\s*[!=+\-*/<>]{1,2}\s*(?:'{1,2}[^']+'{1,2}|\"{1,2}[^\"]+\"{1,2})"
    regex_find_event_start = r"if\s\$*(?:args|ARGS)\[0]\s*=\s*(?:'{1,2}[^']+'{1,2}|\"{1,2}[^\"]+\"{1,2}):"
    regex_find_event_call_beg = r"(?:gt|gs)\s*(?:'{1,2}|\"{1,2})"
    regex_find_event_call_mid = r"(?:'{1,2}|\"{1,2}),\s*(?:'{1,2}|\"{1,2})"
    regex_find_event_call_end = r"(?:'{1,2}|\"{1,2})(?:,\s*(?:'{1,2}|\"{1,2})[^'\"]+(?:'{1,2}|\"{1,2}))"
    regex_find_location_references = r"(?:gs|gt)\s*(?:'|\"){1,2}<<[^<>]+>>(?:'|\"){1,2}"

    files = {}
    filename_variables = []
    filename_arguments = []
    location_references = []

    for file in os.listdir("translated/"):
        file_reference = io.open("translated/" + file, 'r', encoding="utf-8")
        files[file] = file_reference.readlines()
        file_reference.close()

    for file in files:
        i = 0
        while i < len(files[file]):
            line = files[file][i]
            matches = re.findall(regex_find_embedded_filenames, line)
            variables = []
            for match in matches:
                variables.extend(re.findall(regex_embedded_variable, match))

            while len(variables) > 0:
                if "<<RAND" in variables[0] or "<<rand" in variables[0]:
                    variables.pop(0)
                else:
                    variables[0] = variables[0][2:-2].strip()
                    if ".name" in variables[0]:
                        filename_reference = re.search(r"images[/\\].*<<[^>]+>>", line).group(0)
                        new_line = files[file].pop(i).replace(filename_reference, filename_reference.replace(variables[0], variables[0].replace(".name", ".filename")))
                        files[file].insert(i, new_line)
                    if "args" in variables[0] or "ARGS" in variables[0]:
                        filename_arguments.append((file, i, variables.pop(0)))
                    elif variables[0] not in filename_variables:
                        filename_variables.append(variables.pop(0))
                    else:
                        variables.pop(0)

            matches = re.findall(regex_find_location_references, line)
            for match in matches:
                location_references.append(re.findall(regex_embedded_variable, match)[0][2:-2].strip())

            i += 1

    for k, variable in zip(range(len(filename_variables)), filename_variables):
        print("["+str(k+1)+"/"+str(len(filename_variables))+"] Reverting filename translation: " + variable)
        for file in files:
            i = 0
            while i < len(files[file]):
                line = files[file][i]
                matches = re.findall(regex_find_variable_assignment_beg + variable.replace("$", "\\$").replace(".", "\.") + regex_find_variable_assignment_end, line)
                for match in matches:
                    string = extract_from_string(match)[0]
                    original = find_key_by_value(string, _text_)

                    if original != "":
                        if ".name" in variable:
                            new_line = line.replace(match, match.replace(".name", ".filename").replace(string, original))
                            files[file].insert(i + 1, new_line)
                            i += 1
                        else:
                            new_line = files[file].pop(i).replace(match, match.replace(string, original))
                            files[file].insert(i, new_line)

                    elif ".name" in variable:
                        new_line = line.replace(match, match.replace(".name", ".filename"))
                        files[file].insert(i + 1, new_line)
                        i += 1

                i += 1

    for k, occurrence in zip(range(len(filename_arguments)), filename_arguments):
        print("[" + str(k+1) + "/" + str(len(filename_arguments)) + "] Creating filename reference variable for: " + str(occurrence))
        location, index, argument = occurrence
        event_index = index-1
        event_line = files[location][event_index]
        event_line_match = re.search(regex_find_event_start, event_line)
        while event_line_match is None and event_index >= 0:
            if "if" in event_line:
                event_line = event_line[event_line.find(":")+1:]

            reassignment = re.search(regex_find_variable_assignment_beg + argument.lower().replace("$", "\\$").replace("[", "\\[") + regex_find_variable_assignment_end, event_line.lower())
            if reassignment is not None:
                match = reassignment.group(0)
                string = extract_from_string(match)[0]
                original = find_key_by_value(string, _arguments_)
                old_line = files[location].pop(event_index)

                new_line = "\t"*old_line.count("\t") + '$file_reference="' + original + '" & ' + old_line[old_line.rfind("\t")+1:]
                files[location].insert(event_index, new_line)

            event_index -= 1
            event_line = files[location][event_index]
            event_line_match = re.search(regex_find_event_start, event_line)

        if event_line_match is None:
            event_call_value = "[^'\"]+"
        else:
            event_call_value = extract_from_string(event_line_match.group(0))[0]

        argument_index = argument[argument.find("[")+1:argument.find("]")]
        event_call_regex = regex_find_event_call_beg + location[:-5] + regex_find_event_call_mid + event_call_value.replace("$", "\\$").replace(".", "\\.") + regex_find_event_call_end + "{" + argument_index + "}"

        for file in files:
            i = 0
            while i < len(files[file]):
                line = files[file][i]
                match = re.search(event_call_regex, line)
                if match is not None and "$filename_reference=" not in line:
                    match = match.group(0)
                    event_arguments = extract_from_string(match)
                    filename_reference = find_key_by_value(event_arguments[-1], _arguments_)

                    if ".name" in filename_reference:
                        filename_reference = filename_reference.replace(".name", ".filename")

                    if "exec:" in line:
                        filename_reference = "$filename_reference=''" + filename_reference + "'' & " + match
                    else:
                        filename_reference = "\t"*match.count("\t") + '$filename_reference="' + filename_reference + '" & ' + match[match.rfind("\t")+1:]

                    new_line = files[file].pop(i).replace(match, filename_reference)
                    files[file].insert(i, new_line)

                i += 1

        new_line = files[location].pop(index).replace(argument, "$filename_reference")
        files[location].insert(index, new_line)

    for k, variable in zip(range(len(location_references)), location_references):
        print("[" + str(k + 1) + "/" + str(len(location_references)) + "] Fixing location references: " + variable)
        for file in files:
            i = 0
            while i < len(files[file]):
                line = files[file][i]
                matches = re.findall(regex_find_variable_assignment_beg + variable.replace("$", "\\$").replace(".", "\.") + regex_find_variable_assignment_end, line)
                for match in matches:
                    string = extract_from_string(match)[0]
                    original = find_key_by_value(string, _text_)
                    new_line = files[file].pop(i).replace(match, match.replace(string, xml[_locations_][original]))
                    files[file].insert(i, new_line)
                i += 1

    for file in files:
        file_reference = io.open("translated/"+file, 'w', encoding="utf-8")
        for line in files[file]:
            file_reference.write(line)
        file_reference.close()


xml = read_xml_files()
old_xml = old_xml_to_dict(io.open("xml/old.xml", 'r', encoding="utf-8"))
done_file = io.open("done.txt", 'r', encoding="utf-8")
done = [done.replace('\n', '') for done in done_file.readlines()]
done_file.close()
done_file = io.open("done.txt", 'a', encoding="utf-8")

auto = "no"

for qsrc in os.listdir("files/"):
    if qsrc not in done:
        if auto == "manual":
            inp = "y"
        else:
            inp = input("Next file: " + qsrc + ". Continue? ").lower()

        if inp == "auto":
            auto = "manual"
            inp = "y"

        if inp == "y":
            _use_auto_translate_ = False
            done.append(qsrc)
            get_data(qsrc)
            done_file.write(qsrc+"\n")
        elif inp == "a":
            _use_auto_translate_ = True
            _alt_tabbed_ = False
            get_data(qsrc)
            done_file.write(qsrc+"\n")
        elif inp == "s":
            continue
        else:
            exit(-69)

correct_translations()
