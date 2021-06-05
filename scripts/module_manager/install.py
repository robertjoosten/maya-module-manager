from maya import cmds
from maya import mel


ROOT_PACKAGE = __name__.rsplit(".", 1)[0]
SHELF_NAME = "MiscTools"
SHELF_TOOL = {
    "label": "module-manager",
    "command": "import {0}.ui; {0}.ui.show()".format(ROOT_PACKAGE),
    "annotation": "Manage maya modules",
    "image1": "MM_icon.png",
    "sourceType": "python"
}


def shelf():
    """
    Add a new shelf in Maya with the tools that is provided in the SHELF_TOOL
    variable. If the tab exists it will be checked to see if the button is
    already added. If this is the case the previous button will be deleted and
    a new one will be created in its place.
    """
    # get top shelf
    shelf_container = mel.eval("$tmpVar=$gShelfTopLevel")
    shelves = cmds.tabLayout(shelf_container, query=True, childArray=True)

    # create shelf
    if SHELF_NAME not in shelves:
        cmds.shelfLayout(SHELF_NAME, parent=shelf_container)

    # get existing members
    names = cmds.shelfLayout(SHELF_NAME, query=True, childArray=True) or []
    labels = [cmds.shelfButton(n, query=True, label=True) for n in names]

    # delete existing button
    if SHELF_TOOL.get("label") in labels:
        index = labels.index(SHELF_TOOL["label"])
        cmds.deleteUI(names[index])

    # add button
    cmds.shelfButton(style="iconOnly", parent=SHELF_NAME, **SHELF_TOOL)
