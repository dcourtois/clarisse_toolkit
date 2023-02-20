Step-by-step tutorial on how to get auto-completion on the Clarisse Python API in Visual Studio Code.

First step is to extract information from your current Clarisse installation. To do that, use the
[GetCompletion.py](../Scripts/GetCompletion.py) script from this repository:
```
python GetCompletion.py --clarisse_bin_dir "C:\Program Files\Isotropix\Clarisse 5.0 SP10b\Clarisse" --output "C:\Development"
```

This will generate the `C:\Development\ix.py` file, which will act as the `ix` module, which is the Clarisse Python API module.

Now, in order for auto completion to work in Visual Studio Code, you'll need `PyLance` extension (and probably `Python`, not really sure) Once you've got both installed, edit your settings, and add the following options:
```
"python.languageServer": "Pylance",
"python.analysis.extraPaths": [ "C:/Development" ],
```

And now, every script containing `import ix` opened in Visual Studio Code should have autocompletion:
![Python autocomplete](https://github.com/dcourtois/clarisse_toolkit_images/blob/main/ix_autocomplete_vscode.gif?raw=true)
