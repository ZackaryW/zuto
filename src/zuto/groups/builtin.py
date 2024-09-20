import os
import threading
from ..utils import resolve_auto, splitstring
from ..runner import ZutoCtx
from ..group import ZutoGroup
from zuu.stdpkg.subprocess import open_detached
from zuu.stdpkg.time import sleep_until
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

@builtin.cmd("exec", resolve_strings=False)
def _exec(_val: str):
    w = splitstring(_val)
    open_detached(*w)

@builtin.cmd("cmd")
def cmd(_val : str):
    os.system(_val)

@builtin.cmd()
def sleep(until: str):
    sleep_until(until)

@builtin.handler("*")
def lifetime_pre_handle(ctx : ZutoCtx, state : str):
    if state != "before":
        return
    
    if not isinstance(ctx.cmd, dict):
        return

    if "lifetime" not in ctx.cmd:
        return
    
    ctx.meta["windows1"] = gw.getAllWindows()

@builtin.handler("*")
def lifetime_after_handle(ctx : ZutoCtx, state : str):
    if state != "after":
        return

    if "windows1" not in ctx.meta:
        return
    
    
    windows1 = ctx.meta["windows1"]
    windows1d = {w.title: w for w in windows1}
    sleep(1)
    windows2 = gw.getAllWindows()
    remainder_time = ctx.meta["remainder_time"]

    
    def target():
        
        differedWnds = [
            w for w in windows2 
            if w.title and w.title not in windows1d 
            and w not in windows1d.values()
        ]
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

@builtin.cmd()
def lifetime(ctx : ZutoCtx, until : str |int):
    ctx.parentMeta["remainder_time"] = until
    ctx.parentMeta["windows2"] = gw.getAllWindows()