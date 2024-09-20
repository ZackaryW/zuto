from ..group import ZutoGroup
from reldplayer.quick import Global, Console

ext = ZutoGroup()


@ext.prop("ldplayer")
def ldplayer():
    Global()
    return Console.auto()


@ext.cmd("ldrun")
def launchex(ldplayer: Console, id: str | int, pkg: str = None):
    assert isinstance(ldplayer, Console)
    assert id

    if pkg is None:
        ldplayer.launch(id)
    else:
        ldplayer.launchex(name=id, packagename=pkg)


@ext.cmd("ldquit")
def quit(ldplayer: Console, id: str | int = None, all: bool = False):
    assert isinstance(ldplayer, Console)
    if not id:
        ldplayer.quitall()
    else:
        ldplayer.quit(id)
