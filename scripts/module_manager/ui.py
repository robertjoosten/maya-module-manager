import os
import webbrowser
from functools import partial
from PySide2 import QtWidgets, QtGui, QtCore

from module_manager import utils
from module_manager.constants import MAYA_ARGUMENTS


FONT = QtGui.QFont()
FONT.setFamily("Consolas")
BOLT_FONT = QtGui.QFont()
BOLT_FONT.setFamily("Consolas")
BOLT_FONT.setWeight(100)

ICON_PATH = utils.get_icon_path("MM_icon.png")
FILE_ICON_PATH = ":/fileOpen.png"
ORANGE_STYLESHEET = "color: orange; text-align: left"


class MayaModuleDetailArgument(QtWidgets.QWidget):
    def __init__(self, parent, key, value):
        super(MayaModuleDetailArgument, self).__init__(parent)

        # create layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # create key
        label = QtWidgets.QLabel(self)
        label.setFont(BOLT_FONT)
        label.setText(key)
        layout.addWidget(label)

        # create value
        label = QtWidgets.QLabel(self)
        label.setFont(FONT)
        label.setText(value)
        layout.addWidget(label)


class MayaModuleDetail(QtWidgets.QWidget):
    enabled_changed = QtCore.Signal(bool, dict)

    def __init__(self, parent, data):
        super(MayaModuleDetail, self).__init__(parent)

        # variables
        self._data = data
        self._path = self.get_path()

        # create layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(7, 0, 7, 0)
        layout.setSpacing(3)

        # create enabled
        enabled_state = data.get("ENABLED") == "+"

        enabled = QtWidgets.QCheckBox(self)
        enabled.setChecked(enabled_state)
        enabled.setFont(BOLT_FONT)
        enabled.setText(data.get("NAME"))
        enabled.stateChanged.connect(self._emit_enabled_changed)
        enabled.setToolTip("Enable/Disable module")
        layout.addWidget(enabled)

        # create version
        version = QtWidgets.QLabel(self)
        version.setFont(FONT)
        version.setText(data.get("VERSION"))
        version.setFixedWidth(85)
        layout.addWidget(version)

        # create maya version
        maya_version = MayaModuleDetailArgument(self, "Maya Version:", data.get("MAYAVERSION", "-"))
        layout.addWidget(maya_version)

        # create platform
        platform = MayaModuleDetailArgument(self, "Platform:", data.get("PLATFORM", "-"))
        layout.addWidget(platform)

        # create language
        language = MayaModuleDetailArgument(self, "Locale:", data.get("LOCALE", "-"))
        layout.addWidget(language)

        # create path
        browser = QtWidgets.QPushButton(self)
        browser.setEnabled(True if self.path else False)
        browser.setFlat(True)
        browser.setIcon(QtGui.QIcon(FILE_ICON_PATH))
        browser.setFixedSize(QtCore.QSize(18, 18))
        browser.released.connect(partial(webbrowser.open, self.path))
        browser.setToolTip("Open module content path with associated browser")
        layout.addWidget(browser)

    def _emit_enabled_changed(self, state):
        """
        :param bool state:
        """
        data = self.data.copy()
        self.enabled_changed.emit(state, data)

    # ------------------------------------------------------------------------

    @property
    def data(self):
        """
        :return: Data
        :rtype: dict
        """
        return self._data

    @property
    def path(self):
        """
        :return: Path
        :rtype: str
        """
        return self._path

    def get_path(self):
        """
        :return: Path to module
        :rtype: str
        """
        # get path
        path = self.data.get("PATH")

        # if the path is not an absolute path, use the parents path variable
        # to append the relative path to.
        if not os.path.isabs(path):
            path = os.path.join(os.path.dirname(self.parent().path), path)
            path = os.path.abspath(path)

        # open path
        return os.path.normpath(path)

    # ------------------------------------------------------------------------

    def is_compatible(self):
        """
        Validate the data against the current version of Maya ran, the
        platform it's ran on and it's language.

        :return: Validation state
        :rtype: bool
        """
        # validate data against current version of maya, the platform its ran
        for key, value in MAYA_ARGUMENTS.items():
            if key not in self.data:
                continue

            if self.data.get(key) != value:
                return False

        return True


class MayaModuleFileHeader(QtWidgets.QWidget):
    show_all_changed = QtCore.Signal(bool)

    def __init__(self, parent, path, show_all):
        super(MayaModuleFileHeader, self).__init__(parent)

        # create layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # create path
        browser = QtWidgets.QPushButton(self)
        browser.setFlat(True)
        browser.setIcon(QtGui.QIcon(FILE_ICON_PATH))
        browser.setFixedSize(QtCore.QSize(18, 18))
        browser.released.connect(partial(webbrowser.open, path))
        browser.setToolTip("Open module file with associated application")
        layout.addWidget(browser)

        # create text
        button = QtWidgets.QPushButton(self)
        button.setFlat(True)
        button.setFont(BOLT_FONT)
        button.setText(os.path.basename(path))
        button.setStyleSheet(ORANGE_STYLESHEET)
        button.setToolTip(path)
        button.released.connect(self.toggle_check_box)
        layout.addWidget(button)

        # create checkbox
        self._check_box = QtWidgets.QCheckBox(self)
        self._check_box.setFixedWidth(80)
        self._check_box.setFont(FONT)
        self._check_box.setText("show all")
        self._check_box.setChecked(show_all)
        self._check_box.stateChanged.connect(self.show_all_changed.emit)
        layout.addWidget(self._check_box)

    # ------------------------------------------------------------------------

    def toggle_check_box(self):
        """
        Toggle the checked state of the checkbox.
        """
        state = self._check_box.isChecked()
        self._check_box.setChecked(not state)


class MayaModuleFile(QtWidgets.QFrame):
    def __init__(self, parent, path):
        super(MayaModuleFile, self).__init__(parent)

        # variables
        show_all = False
        self._path = path

        # set outline
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)

        # create layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # create header
        header = MayaModuleFileHeader(self, path, show_all=show_all)
        header.show_all_changed.connect(self.manage_module_details)
        layout.addWidget(header)

        # create divider
        divider = utils.divider(self)
        layout.addWidget(divider)

        # check permissions
        if not os.access(path, os.W_OK):
            self.setEnabled(False)

        # add module details
        self.add_module_details()
        self.manage_module_details(show_all)

    # ------------------------------------------------------------------------

    @property
    def path(self):
        """
        :return: Path
        :rtype: str
        """
        return self._path

    # ------------------------------------------------------------------------

    def manage_module_details(self, state):
        """
        Loop all widgets and either display all or filter the ones that are
        capable with the version of Maya that is ran.

        :param bool state:
        """
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if not isinstance(widget, MayaModuleDetail):
                continue

            visible = True if state else widget.is_compatible()
            widget.setVisible(visible)

    def add_module_details(self):
        """
        Populate the widget with module data widgets, one for each module data
        line found in the module file.
        """
        for data in utils.filter_module_file(self.path):
            mod = MayaModuleDetail(self, data)
            mod.enabled_changed.connect(self.update_module_file)
            self.layout().addWidget(mod)

    # ------------------------------------------------------------------------

    def update_module_file(self, state, data):
        """
        :param bool state:
        :param dict data:
        """
        utils.update_module_file(self.path, state, data)


# ----------------------------------------------------------------------------


class MayaModuleManager(QtWidgets.QWidget):
    def __init__(self, parent):
        super(MayaModuleManager, self).__init__(parent)
        
        # set ui
        self.setParent(parent)        
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Maya Module Manager")
        self.setWindowIcon(QtGui.QIcon(ICON_PATH))
        self.resize(700, 400)

        # create container layout
        container = QtWidgets.QVBoxLayout(self)
        container.setContentsMargins(0, 0, 0, 0)
        container.setSpacing(3)

        # create scroll widget
        widget = QtWidgets.QWidget(self)
        self._layout = QtWidgets.QVBoxLayout(widget)
        self._layout.setContentsMargins(3, 3, 3, 3)
        self._layout.setSpacing(3)

        scroll = QtWidgets.QScrollArea(self)
        scroll.setFocusPolicy(QtCore.Qt.NoFocus)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        container.addWidget(scroll)

        # add modules
        self.add_modules()

    # ------------------------------------------------------------------------

    def add_modules(self):
        """
        Populate the widget with module file widgets, one for each module file
        found.
        """
        for path in utils.get_module_file_paths():
            mod = MayaModuleFile(self, path)
            self._layout.addWidget(mod)


def show():
    parent = utils.get_main_window()
    window = MayaModuleManager(parent)
    window.show()
