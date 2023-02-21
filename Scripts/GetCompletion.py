import argparse
import os
import re
import sys

# Main Python version
PYTHON_VERSION = int(sys.version[0])

# indentation used for the output completion file
INDENTATION = "  "

# A few regexes used later
CLASS          = re.compile(r"^<([^; ]+).*>$")
PARAM_TYPE  = re.compile(r"[\w_][\w\d_]*: ('([^']+)')")
RETURN_TYPE = re.compile(r" -> ('(.+)')")

# Global lookup tables of C++ types (as used by Swig Python annotations) to Python types.
TYPES = dict()


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
    return str(inspect.signature(function) if PYTHON_VERSION == 3 else funcsigs.signature(function))


def write_doc(file, indentation, object):
    """Writes the documentation for a thing (object, function, etc.)"""
    string = inspect.getdoc(object)
    if string is None:
        string = inspect.getcomments(object)
    if string is not None:
        write(file, indentation, "\"\"\"")
        lines = string.split("\n")
        for line in lines:
            write(file, indentation, line.strip("# ").strip())
        write(file, indentation, "\"\"\"")


def write_function(file, indentation, name, func):
    """Writes a function + its doc (if any)"""
    write(file, indentation, "def {}{}:".format(name, signature(func)))
    write_doc(file, indentation + 1, func)
    write(file, indentation + 1, "pass")


def is_string(type_str):
    """Small helper that checks if a type string is the type of a string"""
    return type_str == "<class 'base.CoreString'>" or type_str == "<class 'base.CoreBasicString'>" or type_str == "<class 'str'>"


def add_type(cpp_type, python_type):
    """Update the global TYPES dictionary with all variants of a C++ type and the corresponding Python type."""
    global TYPES
    TYPES[cpp_type] = python_type
    TYPES["{} const".format(cpp_type)] = python_type
    TYPES["{} *".format(cpp_type)] = python_type
    TYPES["{} &".format(cpp_type)] = python_type
    TYPES["{} const *".format(cpp_type)] = python_type
    TYPES["{} const &".format(cpp_type)] = python_type
    TYPES["{} *const &".format(cpp_type)] = python_type


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
    "s_empty_handle"
]

# a few suffixes to ignore
IGNORED_SUFFIXES = [
    "____class_destructor__",
    "_class_info",
    "_swigregister"
]

# used by parse to avoid processing the same modules multiple times
processed = []

def parse(file, indentation, module, parent):
    """
    file: ix.py file handle.
    indentation: current level of indentation
    module: the Python module we're currently parsing
    parent: name of the parent module as a string
    """
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
        if parent == "":
            if member[0] == "application":
                write(file, indentation, "application = api.ClarisseApp()")
                continue
            if member[0] == "selection":
                write(file, indentation, "selection = ApplicationSelection()")
                continue

        # functions
        if inspect.isfunction(member[1]) or inspect.ismethod(member[1]) or inspect.isbuiltin(member[1]):
            write_function(file, indentation, member[0], member[1])

        # classes and modules
        elif inspect.ismodule(member[1]) or inspect.isclass(member[1]):
            if member[0] not in processed:
                processed.append(member[0])
                python_type = "{}.{}".format(parent, member[0]) if parent != "" else member[0]
                write(file, indentation, "class {}:".format(member[0]))
                parse(file, indentation + 1, member[1], python_type)
                write(file, indentation + 1, "pass")
                add_type(member[0], python_type)

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


def process_annotations(source_file, destination_file):
    # add builtin C++ types
    add_type("unsigned long long", "int")
    add_type("unsigned long",      "int")
    add_type("unsigned int",       "int")
    add_type("unsigned short",     "int")
    add_type("unsigned char",      "int")
    add_type("long long",          "int")
    add_type("long",               "int")
    add_type("int",                "int")
    add_type("short",              "int")
    add_type("char",               "int")
    add_type("size_t",             "int")
    add_type("float",              "float")
    add_type("double",             "float")
    add_type("bool",               "bool")
    add_type("void",               "None")

    # local helper to match either a param annotation or if not found, the return annotation
    def search(line, start=0):
        res = PARAM_TYPE.search(line, start)
        if not res:
            res = RETURN_TYPE.search(line, start)
        return res

    # and process
    for line in source_file.readlines():
        if line.find("def ") != -1:
            annotation = search(line)
            while annotation:
                cpp_type = annotation[2]
                python_type = TYPES.get(cpp_type)
                new_start = annotation.end()
                if python_type is not None:
                    to_replace = annotation[1]
                    new_start += len(python_type) - len(to_replace)
                    line = line.replace(to_replace, python_type)
                annotation = search(line, new_start)
        destination_file.write(line)


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

    has_annotations      = PYTHON_VERSION == 3 and options.python_major_version == 3
    module_filename      = "{}/ix.py".format(options.output_dir)
    temp_module_filename = "{}.temp".format(module_filename)

    # generate the fake "module"
    file = open(module_filename if has_annotations is False else temp_module_filename, "w")
    print("Generating ix.py...")
    parse(file, 0, ix, "")
    file.close()

    # process annotations
    if has_annotations:
        print("Converting type annotations...")
        source = open(temp_module_filename, "r")
        destination = open(module_filename, "w")
        process_annotations(source, destination)
        source.close()
        destination.close()
        os.remove(temp_module_filename)
