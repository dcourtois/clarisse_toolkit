import os
import sys

# Path to Clarisse
CLARISSE_DIR = "C:/Program Files/Isotropix/Clarisse 5.0 SP1/Clarisse"
# CLARISSE_DIR = "C:/Program Files/Isotropix/Clarisse iFX 4.5/Clarisse"

# Main Python version
PYTHON_VERSION = int(sys.version[0])

# some other Clarisse paths, derived from the previous one.
CLARISSE_MODULE_DIR = "{}/module".format(CLARISSE_DIR)
CLARISSE_PYTHON_DIR = "{}/python{}".format(CLARISSE_DIR, PYTHON_VERSION)

# indentation used for the output completion file
INDENTATION = "  "

# make Clarisse's modules findable
os.environ["PATH"] += os.pathsep + CLARISSE_DIR
sys.path.append(CLARISSE_PYTHON_DIR)

# import things needed for reflection
import inspect
if PYTHON_VERSION == 2:
    import funcsigs

# import our helpers (allow to use `ix.` stuff like if you were inside the script editor in Clarisse)
from ix_helper import *


def write(file, indentation, line):
    """Helper to write a line with indentation"""
    for _ in range(indentation):
        file.write(INDENTATION)
    file.write(line)
    file.write("\n")


def signature(function):
    """Returns the signature of a function as a string"""
    if inspect.isbuiltin(function):
        return "(*args)"
    return inspect.signature(function) if PYTHON_VERSION == 3 else funcsigs.signature(function)


def write_doc(file, indentation, object):
    """Writes the documentation for a thing (object, function, etc.)"""
    string = inspect.getdoc(object)
    if string is None:
        string = inspect.getcomments(object)
    if string is not None:
        write(file, indentation, "\"\"\"")
        for line in string.split("\n"):
            write(file, indentation, line.strip("# "))
        write(file, indentation, "\"\"\"")


def write_function(file, indentation, name, func):
    """Writes a function + its doc (if any)"""
    write(file, indentation, "def {}{}:".format(name, str(signature(func))))
    write_doc(file, indentation + 1, func)
    write(file, indentation + 1, "pass")


def is_string(type_str):
    """Small helper that checks if a type string is the type of a string"""
    return type_str == "<class 'base.CoreString'>" or type_str == "<class 'base.CoreBasicString'>" or type_str == "<class 'str'>"


# a few things that we don't want to process
IGNORED = [
    # system modules
    "os",
    "proxy",
    "ref",
    "sys",
    "weakref",
    # our binding modules (all their stuff is imported inside ix.api)
    "base",
    "framework",
    "gui",
    "helpers",
    # some additional stuff that screw up the generated file
    "cvar",
    # some crappy static members that shouldn't be exposed anyway -_-
    "s_has_custom_data_in_associate_window",
    "s_empty_box",
]

# a few suffixes to ignore
IGNORED_SUFFIXES = [
    "____class_destructor__",
    "_class_info",
    "_swigregister",
]

# used by parse to avoid processing the same modules multiple times
processed = []

def parse(file, indentation, module, parent):
    members = inspect.getmembers(module)
    variables = []
    for member in members:
        # private Python stuff that we don't care about
        if member[0].startswith("_"):
            continue

        # ignore some suffixes
        ignore = False
        for suffix in IGNORED_SUFFIXES:
            if member[0].endswith(suffix):
                ignore = True
                break
        if ignore is True:
            continue

        # ignored stuff
        if member[0] in IGNORED:
            continue

        # special cases
        if parent == "ix":
            if member[0] == "application":
                write(file, indentation, "application = api.ClarisseApp()")
                continue
            if member[0] == "selection":
                write(file, indentation, "selection = ApplicationSelection()")
                continue

        if member[0] == "PARSER_SERIAL_VERSION_TOKEN":
            foo = 0

        # functions
        if inspect.isfunction(member[1]) or inspect.ismethod(member[1]) or inspect.isbuiltin(member[1]):
            write_function(file, indentation, member[0], member[1])

        # classes
        elif inspect.ismodule(member[1]) or inspect.isclass(member[1]):
            if member[0] not in processed:
                processed.append(member[0])
                write(file, indentation, "class {}:".format(member[0]))
                parse(file, indentation + 1, member[1], member[0])
                write(file, indentation + 1, "pass")

        # members
        else:
            type_str = str(type(member[1]))
            if type_str == "<type 'property'>" or type_str == "<class 'property'>":
                variables.append(member[0])
            elif is_string(type_str):
                write(file, indentation, "{} = \"{}\"".format(member[0], str(member[1])))
            else:
                write(file, indentation, "{} = {}".format(member[0], str(member[1])))

    # public write instance members
    # Note: to be able to handle this, we would need to create an instance of the class (type is `parent`) and set assign
    # the default value in this instance. This could be achieved using `eval` but to create generic code, it requires `parent`
    # to be constructible without any parameter (e.g. to be able to write something like `eval("ix.api.{}()".format(parent))`
    # but the first case where this happens (AbcExportOptions) requires additional parameters...
    # And when looking at the generated code so far, it seems that this kind of thing happens veeeery rarely, so for now, just
    # leaving this here because it's not important.
    # TODO: handle special cases like AbcExportOptions' additional constructor parameter
    # TODO: implement the `get_attribute` helper function to retrieve the default value of a var from an object (and handle
    #       the case of strings which need to be in \")
    # if len(variables) > 0:
    #     write(file, indentation, "def __init__(self):")
    #     obj = eval("ix.api.{}()".format(parent))
    #     for variable in variables:
    #         write(file, indentation + 1, "self.{} = {}".format(variable, get_attribute(obj, variable)))


if __name__ == "__main__":
    with open("ix.py", "w") as file:
        write(file, 0, "class ix:")
        parse(file, 1, ix, "ix")
        file.close()
