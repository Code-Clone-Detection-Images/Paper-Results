#!/usr/bin/env python3

import sys
import glob
import os
import string
import random
import re

from typing import Dict, Tuple


# funny, code clones in a paper about them...
JAVA_EXTRACT_CLASSNAMES = re.compile(r"class\s+(?P<name>[$_A-Za-z][$_A-Za-z0-9]*)")
# if collisions are to likely
CLASS_NAME_LENGTH = 25


def random_class_name(length):
    assert length > 0
    letters = string.ascii_letters + string.digits
    # ensure the first one is a valid uppercase letter, we do not use dollar or underscore for that matter
    return random.choice(string.ascii_uppercase) + ''.join(random.choice(letters) for _ in range(length - 1))


def __replace_class_name(match, cls_name) -> str:
    return f"{match.group(1)}{cls_name}{match.group(2)}"


ClassNameMapping = Dict[str, str]
FileNameMapping = Dict[str, str]


class JavaFileHasInvalidClassesException(Exception):
    pass


def __create_java_filename_mapping(java_file: str, name: str) -> Tuple[FileNameMapping, ClassNameMapping]:
    file_name_mapping: FileNameMapping = {}
    class_name_mapping: ClassNameMapping = {}
    # why not find all? it returns strings...
    all_classes = list(JAVA_EXTRACT_CLASSNAMES.finditer(java_file))
    if len(all_classes) == 0:
        raise JavaFileHasInvalidClassesException
    for i, c in enumerate(all_classes):
        new_name = random_class_name(CLASS_NAME_LENGTH)
        if i == 0:  # use first
            file_name_mapping[name] = new_name
        class_name_mapping[all_classes[0]['name']] = new_name

    return file_name_mapping, class_name_mapping


File = str
Name = str


def __apply_java_file_mapping(java_file: str, name: str, mappings: Tuple[FileNameMapping, ClassNameMapping]) -> Tuple[Name, File]:
    # update file name
    name = mappings[0][name] + ".java"
    # update all classes
    for map_from, map_to in mappings[1].items():
        java_file = re.sub(f"([^A-Za-z0-9]){map_from}([^A-Za-z0-9])",
                           lambda m: __replace_class_name(m, map_to), java_file)

    return name, java_file


def __get_file(file: str, output: str) -> None:
    if not os.path.isfile(file):
        return
    lines = ""
    with open(file, mode='r') as f:
        lines = f.read()

    try:
        fln_mapping = __create_java_filename_mapping(lines, file)
    except JavaFileHasInvalidClassesException:
        return

    newfile, newlines = __apply_java_file_mapping(lines, file, fln_mapping)

    with open(os.path.join(output, newfile), mode='w') as f:
        f.write(newlines)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("collect <name> <output>")
        exit(1)

    name = sys.argv[1]
    output = sys.argv[2]
    os.makedirs(output, exist_ok=False)
    for file in glob.iglob("**/" + name + "*", recursive=True):
        try:
            __get_file(file, output)
        except UnicodeDecodeError:
            print("skipping", file)

