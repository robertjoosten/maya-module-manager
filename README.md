# maya-module-manager
Module manager for Maya.

## Installation
* Extract the content of the .rar file anywhere on disk.
* Drag the module-manager.mel file in Maya to permanently install the script.

## Usage
<p align="center"><img src="docs/_images/module-manager-example.png?raw=true"></p>

Modules can be (de)activated by toggling the checkbox **[2]**. The user is also presented with other information regarding the module, its version, the maya version, platform and language. By default the manager will only show you modules that are compatible with the version of Maya you are running, by toggling the `show all` checkbox all modules associated with the file can be edited. Press the folder to open the module file with the associated application. This will make it possible to easily edit the file manually if need be **[4]**.

The file itself can be managed directly by pressing the folder button next to the module filename **[1]**. Doing this will open up the file in the associated application. It is also possible to dive directly into the module code itself by pressing the folder button **[3]**. This will open up the folder of the module content in your browser.

This manager edits the module files on disk, it is possible that the user won't have permissions to edit the module files. If this is the case the module will still be displayed but the widget is disabled preventing the user from editing the file **[5]**.
