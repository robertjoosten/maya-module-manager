from maya import cmds


def main():
    from module_manager import install
    install.shelf()


if not cmds.about(batch=True):
    cmds.evalDeferred(main)
