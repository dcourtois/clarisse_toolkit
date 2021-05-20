Introduction
============

This repository is a collection of some useful (hopefully) Python scripts to use in [Clarisse](https://www.isotropix.com/)
Following is a few paragraphs giving a bit more details on how to use the [Clarissde SDK documentation](https://clarissewiki.com/olympus/sdk/index.html)
and understand a few key things that can help developing Python scripts for Clarisse.

Contributing
============

This repository is a community based effort. I'm not paid to maintain this. It's just there because I thought it might have some use
to others. A few rules if you want to contribute:

1. When creating issue, be precise. Issues like "stuff doesn't work, fix it" will be closed without me taking the time to even try to
understand your problem. If you don't take the time to at least precisely explain your problem, create some repro, etc. don't expect
me to take mine to try to decipher your issue.

2. Pull requests will be accepted provided they are carefully crafted: the code should follow the convention of the existing stuff,
it should be clear and documented, etc.

Clarisse Python API
===================

Disclaimer: the following parts are not meant to be a startup guide to Python scripting. You should at least be familiar with Python
scripting, and ideally you should have already played a bit with Python in Clarisse. This guide is something meant to help you navigate
the documentation and understand the errors, and how to convert C++ stuff to Python.

The first thing to know is that the Python API is automatically generated from the C++ SDK. As such, some errors and some types might
be a bit confusing for people only used to native Python. We'll see how types are "translated" between both languages, then we'll see
how to read the SDK documentation (also generated from C++) and finally how to decode Python errors.

C++ / Python types
==================

### Numbers

In Python, numbers are numbers. In C++, numbers can be integers (no decimals) or floating point values (decimals) Here is a list of some
of the most used types in C++:
- integers: int, unsigned int, long, unsigned long, long long, unsigned long long, char, short, etc.
- floating point numbers: float and double
So basically when you see one of those in C++, it means it should be a number in Python. Easy.

### Strings

In our C++ SDK, strings have the type `CoreString`. Automatic conversion between `CoreString` and the native Python string is usually done,
so whenever you see `CoreString` in the C++ documentation, you can use a usual string.

### Arrays

This is a bit trickier. In Python when you create a `list` you can add basically whatever you like in it. In C++, it doesn't work like this:
when you create the equivalent of a list, you specify the type of the data the list will hold. And you won't be able to add anything which is
not of that type inside.

In C++, we have various types of lists: `CoreBasicArray<T>`, `CoreArray<T>` and `CoreArray<T>`. Now, this syntax is a bit strange for Python,
but in C++ basically the thing inside the `<...>` tells the type of the data that the list of dict will hold.

For instance, `CoreVector<int>` will be a list of integers. You won't be able to add a string to it for instance. And since Python doesn't
support the `<...>` syntax, those list and dict types are converted in Python using the following convention.
1. The type of the data comes first, always starting with an upper case
2. Special case for integers: when the type is `unsigned`, in Python you just prefix by `U` (e.g. `unsigned int` gives `UInt`)
3. The type end by the type of the list without its `Core` prefix. So `Vector` for `CoreVector`, `Array` for `CoreArray`, etc.

So, with this knowledge, let's take a look at some examples that you might find:
- `CoreArray<unsigned short>` gives `UShortArray`
- `CoreVector<CoreString>` gives `CoreStringVector`
etc.

Reading types
=============

When writting scripts, one of the most important thing is to know the types of the objects you are manipulating. It's quite easy to do using the
native `type` function:
```python
print(type(ix.application), type(ix.api.CoreString("foo")))

# outputs:
# (<class 'gui.ClarisseApp'>, <class 'base.CoreString'>)
```

This will print the types of the objects in the form `<module_name>.<class_name>`. The `module_name` is not really needed, but the `class_name` is
very important: this is the name to look for in the Clarisse SDK documentation (see next section)

So whenever you have an object and wonder how to manipulate it:
1. `print(type(my_object))`
2. look the class up in the documentation to see what you can do with it.

Using the SDK documentation
===========================

So, now you want to know what you can do with your object `ix.application`. You now know its type `ClarisseApp`, so you can go the documentation
and click on the `Classes` tab which contains the list of all the SDK classes (most of them are exposed in Python)
https://clarissewiki.com/olympus/sdk/annotated.html

In this page, you can either use the search bar on the upper right corner, or manually search for the class you're interested in. In our case,
you'll end up here: https://clarissewiki.com/olympus/sdk/class_clarisse_app.html

This is the documentation page for the class `ClarisseApp`. In contains everything that is usable for this class. The first part is the inheritance
diagram of the class: `ClarisseApp` inherit from `GuiApp` (meaning it can do what `GuiApp` can) which inherits from `AppObject`, etc.

After that are the methods of `ClarisseApp`. And after the list of methods, there are a few lines looking like `Public Member Functions inherited
from ...`. When you click on those lines, you will see the methods inherited from base classes. For instance if you click on the member functions
inherited from `AppBase` and look at the end, you'll see a `get_version` method. This means that a `ClarisseApp` object can call this `get_version`
method:
```python
print(ix.application.get_version())

# outputs:
# 4.0.0.0.9
```

Now, let's see how to convert those C++ documentation to Python. We'll take 2 methods as example:
```cpp
virtual CoreArray< CoreString > get_recent_files (const CoreString &type) const =0
virtual void                    add_recent_file (const CoreString &path, const CoreString &type)=0
```

First thing is to ignore stuff that are specific to C++: `virtual`, `const`, `&`. Those are qualifiers that do not have real equivalent in Python, so
just ignore them. In the same manner, the `=0` at the end can be ignored. This will leave you with:
```cpp
CoreArray< CoreString > get_recent_files (CoreString type)
void                    add_recent_file (CoreString path, CoreString type)
```

This looks more like a function. The main difference compared to Python is that you have the returned type before the function name (`void`
means the function returns nothing) and each function argument has its type before its name. So for instance,
`CoreArray< CoreString > get_recent_files (CoreString type)` is a function named `get_recent_files` which takes a string as its argument, and will return
an array of strings.

Now these methods have no documentation, so you're left to guessing what the arguments and return values do. Some other methods are documented (for
instance the documentation for `GuiApp::open_file`: https://clarissewiki.com/olympus/sdk/class_gui_app.html#ac710a660a8bee11df8edafdbecbecf6c)
When a method is not documented, usually the names of the arguments kinda give a hint as to what they are, but in case it doesn't (which is the
case for the `get_recent_files`) you can still try to find some info.

In this example, you can check in the Clarisse installation directory: the menus and shelves are Python scripts. And if you search for `get_recent_file`
you'll find a hit in `menus/main_menu/file/_show.py`, where there are 2 calls to this method, one for the recent projects, one for the recent references,
and so judging from those 2 calls, `type` is either `project` to get the recent project files, or `reference` to get the recent referenced files.

This was just an example of how to navigate the documentation. Hopefully the documentation improves overtime.
