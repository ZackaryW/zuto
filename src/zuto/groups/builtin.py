from ..utils import resolve_auto
from ..runner import ZutoCtx
from ..group import ZutoGroup
from zuu.stdpkg.subprocess import open_detached
from zuu.stdpkg.time import sleep_until

builtin = ZutoGroup("builtin")


@builtin.cmd("first", scope="*", resolve_strings=False)
def first(ctx: ZutoCtx, args: list):
    done = False
    for arg in args:
        try:
            args = resolve_auto(args, ctx.env)
            ctx.runner.run(arg)
            done = True
            break
        except:  # noqa
            pass

    if not done:
        raise ValueError("no command found")


@builtin.cmd()
def exec(cmd: str, *args):
    open_detached(cmd, *args)


@builtin.cmd()
def sleep(until: str):
    sleep_until(until)
