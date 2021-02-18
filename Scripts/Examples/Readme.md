
Each example starts by a docstring describing the content of the example. If an example needs to be customized before being
used, it's specified in the docstring, so read them. For instance most of the example currently use the
[QtHelper.py](../QtHelper.py) script and thus need to be customized to be able to find it.

If I find a way to make this a lot more user friendly, I'll do it, but I could find any way (it comes from the fact that
when Clarisse executes a script, it executes from a string, so you don't have access to the usual `__file__` variable,
so I can't use relative paths nore compute one from the current script)
