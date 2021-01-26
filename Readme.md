Introduction
============

This repository is a collection of some useful (hopefully) Python scripts to use in [Clarisse](https://www.isotropix.com/)
Following is a few paragraphs giving a bit more details on how to use the [Clarissde SDK documentation](https://clarissewiki.com/olympus/sdk/index.html)
and understand a few key things that can help developing Python scripts for Clarisse.

Disclaimer: the following part is not meant to be a startup guide to Python scripting. You should at least be familiar with Python
scripting, and ideally you should have already played a bit with Python in Clarisse. This guide is something meant to help you navigate
the documentation and understand the errors, and how to convert C++ stuff to Python.

Clarisse Python API
===================

The first thing to know is that the Python API is automatically generated from our C++ SDK. As such, some errors and some types might
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

In Clarisse, when you print most of our objects, what's printed is the type of the object. For instance:
```python
print(ix.application)

# outputs:
# <gui.ClarisseApp; proxy of <Swig Object of type 'ClarisseApp *' at 0x0000023B30FF7240> >
```

The important part is the first: `gui.ClarisseApp`. `gui` is the module in which the type is, and `ClarisseApp` is the class name of the object.
This kind of outputs is important because you will probably encounter them a lot in error messages when working on new scripts.

Some other types are printed in a friendler manner. For instance:
```python
string = ix.api.CoreString("foo")
print(string)

# outputs:
# foo
```

You can still use the `type` Python function to get the type of both kind of objects:
```python
print(type(ix.application), type(ix.api.CoreString("foo")))

# outputs:
# (<class 'gui.ClarisseApp'>, <class 'base.CoreString'>)
```

This is a lot simpler. You only have the type, and it's always in the form `<module_name>.<class_name>`.

Using the SDK documentation
===========================

So, now you want to know what you can do with your object `ix.application`. You now know its type `ClarisseApp`, so you can go the documentation
and click on the `Classes` tab which contains the list of all the SDK classes (most of them are exposed in Python)
https://clarissewiki.com/olympus/sdk/annotated.html

In this page, you can either use the search bar on the upper right corner, or manually search for the class you're interested in. In our case,
you'll end up here: https://clarissewiki.com/olympus/sdk/class_clarisse_app.html

This is the documentation page for the class `ClarisseApp`. In contains everything that is usable for this class. The first part is the inheritance
diagram of the class: `ClarisseApp` inherit from `GuiApp` (meaning it can do what `GuiApp` can) which inherits from `AppObject`, etc.

After that are the methods of `ClarisseApp`. And after the list of methods, there is a few lines looking like `Public Member Functions inherited
from ...`. When you click on those lines, you will see the methods inherited from base classes. For instance if you click on the member functions
inherited from `AppBase` and look at the end, you'll see a `get_version` method. And surely enough:
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

First thing is to ignore stuff that are specific to C++: `virtual`, `const`, `&`. Those are qualifiers that have real equivalent in Python, so
just ignore them. In the same manner, the `=0` at the end can be ignored. This will leave you with:
```cpp
CoreArray< CoreString > get_recent_files (CoreString type)
void                    add_recent_file (CoreString path, CoreString type)
```

Now this looks more like a function. The main difference compared to Python is that you have the returned type before the function name (`void`
means the function returns nothing) and each function argument has its type before its name. So for instance,
`CoreArray< CoreString > get_recent_files (CoreString type)` is a function named `get_recent_files` which takes a string as its argument, and will return
an array of strings.
