import os
import sys
import subprocess
from maya import cmds, OpenMayaUI


# ----------------------------------------------------------------------------


# import pyside, do qt version check for maya 2017 >
qtVersion = cmds.about(qtVersion=True)
if qtVersion.startswith("4") or type(qtVersion) not in [str, unicode]:
    from PySide.QtGui import *
    from PySide.QtCore import *
    import shiboken
else:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    import shiboken2 as shiboken


# ----------------------------------------------------------------------------


FONT = QFont()
FONT.setFamily("Consolas")

BOLT_FONT = QFont()
BOLT_FONT.setFamily("Consolas")
BOLT_FONT.setWeight(100)


# ----------------------------------------------------------------------------


ORANGE_STYLESHEET = "color: orange; text-align: left"


# ----------------------------------------------------------------------------


MODULE_ARGUMENTS = [
    "MAYAVERSION",
    "PLATFORM",
    "LOCALE",
]

MAYA_ARGUMENTS = {
    "MAYAVERSION": cmds.about(version=True),
    "PLATFORM": cmds.about(operatingSystem=True),
    "LOCALE": cmds.about(uiLanguage=True),
}


# ----------------------------------------------------------------------------


def mayaWindow():
    """
    Get Maya's main window.

    :rtype: QMainWindow
    """
    window = OpenMayaUI.MQtUtil.mainWindow()
    window = shiboken.wrapInstance(long(window), QMainWindow)

    return window


def getIconPath(name):
    """
    Get an icon path based on file name. All paths in the XBMLANGPATH variable
    processed to see if the provided icon can be found.

    :param str name:
    :return: Icon path
    :rtype: str/None
    """
    for path in os.environ.get("XBMLANGPATH").split(os.pathsep):
        iconPath = os.path.join(path, name)
        if os.path.exists(iconPath):
            return iconPath.replace("\\", "/")


# ----------------------------------------------------------------------------


def divider(parent):
    """
    Create divider ui widget.

    :param QWidget parent:
    :rtype: QFrame
    """
    line = QFrame(parent)
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    return line


# ----------------------------------------------------------------------------


def getModulePaths():
    """
    :return: Maya module paths
    :rtype: list
    """
    return os.environ.get("MAYA_MODULE_PATH").split(os.pathsep)


def getModuleFiles():
    """
    :return: Maya module files
    :rtype: list
    """
    # variable
    modules = []

    # loop module paths
    for path in getModulePaths():
        # make sure path exists, by default maya adds paths to the variable
        # that don't necessarily have to exist.
        if not os.path.exists(path):
            continue

        # extend modules
        modules.extend(
            [
                os.path.normpath(os.path.join(path, f))
                for f in os.listdir(path) or []
                if f.lower().endswith("mod") and not f.startswith("moduleManager")
            ]
        )

    # sort modules by file name
    modules.sort(key=lambda x: os.path.basename(x))

    return modules


# ----------------------------------------------------------------------------


def parseModuleLine(line):
    """
    Parse the line of a module, the line needs to start with either a + or a -
    if this is not the case it means it is additional information that belongs
    to the module which is defined in the lines above this one. If that is the
    case None is returned.

    :param str line:
    :return: Module data
    :rtype: generator
    """
    # validate line
    if len(line) < 1 or line[0] not in ["+", "-"]:
        return

    # variable
    data = {}
    partitions = line.split()

    # copy partitions to loop and be able to remove from the original list
    # without messing with the loop
    for partition in reversed(partitions):
        for argument in MODULE_ARGUMENTS:
            if not partition.startswith(argument):
                continue

            data[argument] = partition[len(argument)+1:]
            partitions.remove(partition)

    # validate length of partitions
    if len(partitions) != 4:
        return

    # add additional data
    for i, key in enumerate(["ENABLED", "NAME", "VERSION", "PATH"]):
        data[key] = partitions[i]

    return data


def filterModuleFile(path):
    """
    :param str path:
    :return: Module data
    :rtype: generator
    """
    # read module file
    lines = readModuleFile(path)

    # filter content
    for line in lines:
        data = parseModuleLine(line)
        if not data:
            continue

        yield data


def readModuleFile(path):
    """
    :param str path:
    :return: Module content
    :rtype: list
    """
    # read file
    with open(path, "r") as f:
        lines = f.readlines()
        lines = [x.strip() for x in lines]

    return lines


def updateModuleFile(path, state, data):
    """
    Update state of module, the module file gets read and the each line will
    be checked if it matches up with the data provided. If it does, that is
    the line that needs its state updated.

    :param str path:
    :param bool state:
    :param dict data:
    """
    # prepare state
    enabled = "+" if state else "-"

    # prepare data for comparison
    del data["ENABLED"]

    # read existing file
    content = []
    lines = readModuleFile(path)

    for line in lines:
        # parse line
        lineData = parseModuleLine(line)

        # validate line
        if lineData:
            # remove enabled for comparison
            del lineData["ENABLED"]

            # validate line data with provided data
            if data == lineData:
                content.append(enabled + line[1:])
                continue

        # store original line
        content.append(line)

    # add new line to content
    content = ["{}\n".format(c) for c in content]

    # write to file
    with open(path, "w") as f:
        f.writelines(content)
