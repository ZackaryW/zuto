import os
import threading
from time import sleep
import typing
from ..utils import resolve_auto, splitstring
from ..runner import ZutoCtx
from ..group import ZutoGroup
from zuu.stdpkg.subprocess import open_detached
from zuu.stdpkg.time import sleep_until, remaining_time
import pygetwindow as gw
builtin = ZutoGroup("builtin")


@builtin.cmd("first", scope="*", resolve_strings=False)
def first(ctx: ZutoCtx, args: list):
    done = False
    e = None
    for i, arg in enumerate(args):
        try:
            print(f"attempting {i+1}/{len(args)}")
            arg = resolve_auto(arg, ctx.env)
            ctx.runner.run(arg)
            done = True
            break
        except Exception as ve:  # noqa
            e = ve
        
    if not done:
        if e:
            raise e
        raise ValueError("no command found")
            

@builtin.cmd("debug")
def debug():
    from zuu.stdpkg.logging import basic_debug
    basic_debug()

@builtin.cmd()
def echo(obj):
    print(obj)

@builtin.cmd("eval")
def _eval(ctx : ZutoCtx, code : str):
    if "import" in code:
        raise ValueError("import is not allowed")
    exec(code, ctx.env)
    # get initial var name
    varname = code.split("=")[0].strip()
    return ctx.env[varname]

@builtin.cmd("exec")
def _exec(cmd: str):
    w = splitstring(cmd)
    open_detached(*w)

@builtin.cmd("os")
def _os(val : str):
    os.system(val)

@builtin.cmd("sleep")
def _sleep(until: str):
    sleep_until(until)

@builtin.handler("*")
def lifetime_pre_handle(ctx : ZutoCtx, state : str):
    if state != "before":
        return
    
    if not isinstance(ctx.cmd, dict):
        return

    if "lifetime" not in ctx.cmd:
        return
    
    ctx.meta["windows1"] = {w._hWnd : w for w in gw.getAllWindows() if w.title}
    

@builtin.cmd()
def lifetime(ctx : ZutoCtx, until : str |int):
    sleep(1)
    def target():
        remainder_time = remaining_time(until)
        windows1 : typing.Dict[str, gw.Win32Window] = ctx.meta["windows1"].copy()
        sleep(0.5)
        windows2 = {w._hWnd : w for w in gw.getAllWindows() if w.title}
        differedWnds = set(windows2.keys()) - set(windows1.keys())
        differedWnds = [windows2[k] for k in differedWnds]

        if len(differedWnds) == 0:
            return
        print(f"scheduled to kill {len(differedWnds)} windows ({differedWnds[0].title}...)")

        sleep_until(remainder_time)
        
        for w in differedWnds:
            w.close()
            print(f"killing window: {w.title} after {remainder_time}")

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()