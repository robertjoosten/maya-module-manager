from maya import cmds


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
