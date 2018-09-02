import os
import webbrowser
from functools import partial

from maya import cmds
from . import utils


# ----------------------------------------------------------------------------


ICON_PATH = utils.getIconPath("MM_icon.png")
FILE_ICON_PATH = ":/fileOpen.png"


# ----------------------------------------------------------------------------


class MayaModuleDetailArgument(utils.QWidget):
    def __init__(self, parent, key, value):
        utils.QWidget.__init__(self, parent)

        # create layout
        layout = utils.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # create key
        label = utils.QLabel(self)
        label.setFont(utils.BOLT_FONT)
        label.setText(key)
        layout.addWidget(label)

        # create value
        label = utils.QLabel(self)
        label.setFont(utils.FONT)
        label.setText(value)
        layout.addWidget(label)


class MayaModuleDetail(utils.QWidget):
    enabledChanged = utils.Signal(bool, dict)

    def __init__(self, parent, data):
        utils.QWidget.__init__(self, parent)

        # variables
        self._data = data
        self._path = self.getPath()

        # create layout
        layout = utils.QHBoxLayout(self)
        layout.setContentsMargins(7, 0, 7, 0)
        layout.setSpacing(3)

        # create enabled
        enabledState = True if data.get("ENABLED") == "+" else False

        enabled = utils.QCheckBox(self)
        enabled.setChecked(enabledState)
        enabled.setFont(utils.BOLT_FONT)
        enabled.setText(data.get("NAME"))
        enabled.stateChanged.connect(self._emitEnabledChanged)
        enabled.setToolTip("Enable/Disable module")
        layout.addWidget(enabled)

        # create version
        version = utils.QLabel(self)
        version.setFont(utils.FONT)
        version.setText(data.get("VERSION"))
        version.setFixedWidth(85)
        layout.addWidget(version)

        # create maya version
        mayaVersion = MayaModuleDetailArgument(
            self,
            "Maya Version:",
            data.get("MAYAVERSION", "-")
        )
        layout.addWidget(mayaVersion)

        # create platform
        platform = MayaModuleDetailArgument(
            self,
            "Platform:",
            data.get("PLATFORM", "-")
        )
        layout.addWidget(platform)

        # create language
        language = MayaModuleDetailArgument(
            self,
            "Locale:",
            data.get("LOCALE", "-")
        )
        layout.addWidget(language)

        # create path
        f = utils.QPushButton(self)
        f.setEnabled(True if self.path else False)
        f.setFlat(True)
        f.setIcon(utils.QIcon(FILE_ICON_PATH))
        f.setFixedSize(utils.QSize(18, 18))
        f.released.connect(self.openPathToModule)
        f.setToolTip("Open module content path with associated browser")
        layout.addWidget(f)

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

    def getPath(self):
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

    def _emitEnabledChanged(self, state):
        """
        :param bool state:
        """
        # copy data data
        data = self.data.copy()

        # emit signal
        self.enabledChanged.emit(state, data)

    # ------------------------------------------------------------------------

    def openPathToModule(self):
        """
        Open the path of the module in the file browser.
        :raise ValueError: When path to module doesn't exist
        """
        if not os.path.exists(self.path):
            raise ValueError("Path to module doesn't exist!")

        webbrowser.open(self.path)

    # ------------------------------------------------------------------------

    def isCompatible(self):
        """
        Validate the data against the current version of Maya ran, the
        platform it's ran on and it's language.

        :return: Validation state
        :rtype: bool
        """
        # validate data against current version of maya, the platform its ran
        for key, value in utils.MAYA_ARGUMENTS.iteritems():
            if key not in self.data:
                continue

            if self.data.get(key) != value:
                return False

        return True


# ----------------------------------------------------------------------------


class MayaModuleFileHeader(utils.QWidget):
    showAllChanged = utils.Signal(bool)

    def __init__(self, parent, path, showAll):
        utils.QWidget.__init__(self, parent)

        # create layout
        layout = utils.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # create path
        f = utils.QPushButton(self)
        f.setFlat(True)
        f.setIcon(utils.QIcon(FILE_ICON_PATH))
        f.setFixedSize(utils.QSize(18, 18))
        f.released.connect(partial(webbrowser.open, path))
        f.setToolTip("Open module file with associated application")
        layout.addWidget(f)

        # create text
        button = utils.QPushButton(self)
        button.setFlat(True)
        button.setFont(utils.BOLT_FONT)
        button.setText(os.path.basename(path))
        button.setStyleSheet(utils.ORANGE_STYLESHEET)
        button.setToolTip(path)
        button.released.connect(self.toggleCheckBox)
        layout.addWidget(button)

        # create checkbox
        self._checkbox = utils.QCheckBox(self)
        self._checkbox.setFixedWidth(80)
        self._checkbox.setFont(utils.FONT)
        self._checkbox.setText("show all")
        self._checkbox.setChecked(showAll)
        self._checkbox.stateChanged.connect(self.showAllChanged.emit)
        layout.addWidget(self._checkbox)

    # ------------------------------------------------------------------------

    def toggleCheckBox(self):
        """
        Toggle the checked state of the checkbox.
        """
        self._checkbox.setChecked(not self._checkbox.isChecked())


class MayaModuleFile(utils.QFrame):
    def __init__(self, parent, path):
        utils.QFrame.__init__(self, parent)

        # variables
        showAll = False
        self._path = path

        # set outline
        self.setFrameShape(utils.QFrame.Box)
        self.setFrameShadow(utils.QFrame.Sunken)

        # create layout
        layout = utils.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # create header
        header = MayaModuleFileHeader(self, path, showAll=showAll)
        header.showAllChanged.connect(self.manageModuleDetails)
        layout.addWidget(header)

        # create divider
        divider = utils.divider(self)
        layout.addWidget(divider)

        # check permissions
        if not os.access(path, os.W_OK):
            self.setEnabled(False)

        # add module details
        self.addModuleDetails()
        self.manageModuleDetails(showAll)

    # ------------------------------------------------------------------------

    @property
    def path(self):
        """
        :return: Path
        :rtype: str
        """
        return self._path

    # ------------------------------------------------------------------------

    def manageModuleDetails(self, state):
        """
        Loop all widgets and either display all or filter the ones that are
        capable with the version of Maya that is ran.

        :param bool state:
        """
        for i in range(self.layout().count()):
            # get widget
            widget = self.layout().itemAt(i).widget()

            # check widget type
            if not isinstance(widget, MayaModuleDetail):
                continue

            # set widget visibility
            visible = True if state else widget.isCompatible()
            widget.setVisible(visible)

    def addModuleDetails(self):
        """
        Populate the widget with module data widgets, one for each module data
        line found in the module file.
        """
        for data in utils.filterModuleFile(self.path):
            mod = MayaModuleDetail(self, data)
            mod.enabledChanged.connect(self.updateModuleFile)
            self.layout().addWidget(mod)

    # ------------------------------------------------------------------------

    def updateModuleFile(self, state, data):
        """
        :param bool state:
        :param dict data:
        """
        utils.updateModuleFile(self.path, state, data)


# ----------------------------------------------------------------------------


class MayaModuleManager(utils.QWidget):
    def __init__(self, parent):
        utils.QWidget.__init__(self, parent)
        
        # set ui
        self.setParent(parent)        
        self.setWindowFlags(utils.Qt.Window)  

        self.setWindowTitle("Maya Module Manager")
        self.setWindowIcon(utils.QIcon(ICON_PATH))
        
        self.resize(700, 400)

        # create container layout
        container = utils.QVBoxLayout(self)
        container.setContentsMargins(0, 0, 0, 0)
        container.setSpacing(3)

        # create scroll widget
        widget = utils.QWidget(self)
        self._layout = utils.QVBoxLayout(widget)
        self._layout.setContentsMargins(3, 3, 3, 3)
        self._layout.setSpacing(3)

        scroll = utils.QScrollArea(self)
        scroll.setFocusPolicy(utils.Qt.NoFocus)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        container.addWidget(scroll)

        # add modules
        self.addModules()

    # ------------------------------------------------------------------------

    def addWidget(self, widget):
        """
        :param QWidget widget:
        """
        self._layout.addWidget(widget)

    # ------------------------------------------------------------------------

    def addModules(self):
        """
        Populate the widget with module file widgets, one for each module file
        found.
        """
        for path in utils.getModuleFiles():
            mod = MayaModuleFile(self, path)
            self.addWidget(mod)


# ----------------------------------------------------------------------------


def show():
    dialog = MayaModuleManager(utils.mayaWindow())
    dialog.show()
