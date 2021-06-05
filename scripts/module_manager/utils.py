import os
import shiboken2
from six import integer_types
from maya import OpenMayaUI
from PySide2 import QtWidgets, QtGui, QtCore

from module_manager.constants import MODULE_ARGUMENTS


def get_main_window():
    """
    :return: Maya main window
    :rtype: QtWidgets.QMainWindow/None
    :raise RuntimeError: When the main window cannot be obtained.
    """
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    ptr = integer_types[-1](ptr)
    if ptr:
        return shiboken2.wrapInstance(ptr, QtWidgets.QMainWindow)

    raise RuntimeError("Failed to obtain a handle on the Maya main window.")


def get_icon_path(file_name):
    """
    Get an icon path based on file name. All paths in the XBMLANGPATH variable
    processed to see if the provided icon can be found.

    :param str file_name:
    :return: Icon path
    :rtype: str/None
    """
    for directory in os.environ["XBMLANGPATH"].split(os.pathsep):
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            return file_path.replace("\\", "/")


# ----------------------------------------------------------------------------


def divider(parent):
    """
    :param QtWidgets.QWidget parent:
    :rtype: QtWidgets.QFrame
    """
    line = QtWidgets.QFrame(parent)
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    return line


# ----------------------------------------------------------------------------


def get_module_paths():
    """
    :return: Maya module paths
    :rtype: list[str]
    """
    return os.environ["MAYA_MODULE_PATH"].split(os.pathsep)


def get_module_file_paths():
    """
    :return: Maya module files
    :rtype: list[str]
    """
    # variable
    modules = []

    # loop module paths
    for path in get_module_paths():
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


def parse_module_line(line):
    """
    Parse the line of a module, the line needs to start with either a + or a -
    if this is not the case it means it is additional information that belongs
    to the module which is defined in the lines above this one. If that is the
    case None is returned.

    :param str line:
    :return: Module data
    :rtype: dict/None
    """
    # validate line
    if len(line) < 1 or line[0] not in {"+", "-"}:
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


def filter_module_file(file_path):
    """
    :param str file_path:
    :return: Module data
    :rtype: generator
    """
    # read module file
    lines = read_module_file(file_path)

    # filter content
    for line in lines:
        data = parse_module_line(line)
        if not data:
            continue

        yield data


def read_module_file(file_path):
    """
    :param str file_path:
    :return: Module content
    :rtype: list
    """
    # read file
    with open(file_path, "r") as f:
        lines = f.readlines()
        lines = [x.strip() for x in lines]

    return lines


def update_module_file(file_path, state, data):
    """
    Update state of module, the module file gets read and the each line will
    be checked if it matches up with the data provided. If it does, that is
    the line that needs its state updated.

    :param str file_path:
    :param bool state:
    :param dict data:
    """
    # prepare state
    enabled = "+" if state else "-"

    # prepare data for comparison
    del data["ENABLED"]

    # read existing file
    content = []
    lines = read_module_file(file_path)

    for line in lines:
        # parse line
        line_data = parse_module_line(line)

        # validate line
        if line_data:
            # remove enabled for comparison
            del line_data["ENABLED"]

            # validate line data with provided data
            if data == line_data:
                content.append(enabled + line[1:])
                continue

        # store original line
        content.append(line)

    # add new line to content
    content = ["{}\n".format(c) for c in content]

    # write to file
    with open(file_path, "w") as f:
        f.writelines(content)
