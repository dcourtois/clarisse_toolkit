import argparse
import os
import re
import sys

# Main Python version
PYTHON_VERSION = int(sys.version[0])

# indentation used for the output completion file
INDENTATION = "  "

# Regex used to identify classes
CLASS = re.compile(r"^<([^; ]+).*>$")


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
                match = CLASS.match(str(member[1]))
                member_type = "{}()".format(match[1]) if match else member[1]
                if match and member_type.startswith("framework."):
                    # TODO: can't do that for some reasons
                    # member_type = "ix.api.{}".format(member_type)
                    continue
                write(file, indentation, "{} = {}".format(member[0], str(member_type)))

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
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="\n".join([
            "Command line tool used to extract the 'ix' Python module from Clarisse's scripting, and export it in",
            "a convenient 'ix.py', so that you can then configure your Python IDE to benefit from",
            "autocompletion.",
        ]))

    parser.add_argument("--clarisse_bin_dir", required=True, type=str, help="Full path to where Clarisse executable is installed.")
    parser.add_argument("--output_dir", required=True, type=str, help="Full path to the directory in which the 'ix.py' file will be generated. The directory must exist and be writable.")
    parser.add_argument("--python_major_version", type=int, default=PYTHON_VERSION, help="Select which major Python version you want to generate the 'ix.py' of. Default is %(default)s")

    options = parser.parse_args(sys.argv[1:])

    # compute the python directory
    clarisse_python_dir = "{}/python{}".format(options.clarisse_bin_dir, options.python_major_version)
    if not os.path.exists(clarisse_python_dir):
        print("Clarisse's Python module directory not found: '{}'".format(clarisse_python_dir))
        print("Please ensure that Clarisse bin dir option is correct, and Clarisse version is at least 5.0.")
        sys.exit(1)

    # make Clarisse's modules findable
    os.environ["PATH"] += os.pathsep + options.clarisse_bin_dir
    sys.path.append(clarisse_python_dir)

    # import things needed for reflection
    import inspect
    if PYTHON_VERSION == 2:
        import funcsigs

    # import our helpers (allow to use `ix.` stuff like if you were inside the script editor in Clarisse)
    from ix_helper import *

    with open("{}/ix.py".format(options.output_dir), "w") as file:
        parse(file, 0, ix, "ix")
        file.close()
