from functools import cached_property
import inspect
from types import MappingProxyType
import typing

from zuto import logger

from .i import ZutoCtxI
from .model import ZutoCmd
from .utils import match_scope, resolve_auto, resolve_special_var


class ZutoGroup:
    def __init__(self, name: str = None):
        self.__name = name or __name__
        self.__cmds: typing.Dict[str, ZutoCmd] = {}
        self.__handlers: typing.Dict[str, typing.List[typing.Callable]] = {}
        self.__signals: typing.Dict[str, typing.List[typing.Callable]] = {}
        self.__props: typing.Dict[str, typing.Callable] = {}

    def __enforce_rules__(self):
        pass

    @property
    def name(self):
        return self.__name

    @property
    def props(self):
        return MappingProxyType(self.__props)

    def prop(self, name: str):
        def decorator(func):
            self.__props[name] = func
            return func

        self.__enforce_rules__()
        return decorator

    @cached_property
    def cmds(self):
        return MappingProxyType(self.__cmds)

    def cmd(self, name: str = None, scope: str = None, resolve_strings: bool = True):
        def decorator(func):
            name2 = name if name else func.__name__
            if name2 in ["val", "cmd"]:
                raise ValueError("reserved command name")
            if name2.startswith("_"):
                raise ValueError("command name cannot start with '_'")
            self.__cmds[name2] = ZutoCmd(
                name=name2, func=func, scope=scope, resolve_strings=resolve_strings
            )
            return func

        self.__enforce_rules__()
        return decorator

    @cached_property
    def handlers(self):
        return MappingProxyType(self.__handlers)

    def handler(self, pattern: str):
        def decorator(func):
            if pattern not in self.__handlers:
                self.__handlers[pattern] = []

            self.__handlers[pattern].append(func)
            self.__enforce_rules__()
            return func

        return decorator

    @cached_property
    def signals(self):
        return MappingProxyType(self.__signals)

    def signal(self, name: str):
        def decorator(func):
            if name not in self.__signals:
                self.__signals[name] = []

            self.__signals[name].append(func)
            self.__enforce_rules__()
            return func

        return decorator

    def invokeSignal(self, name: str, ctx):
        if name in self.__signals:
            for func in self.__signals[name]:
                func(ctx)

    def invokeHandler(self, ctx, pattern: str, state: str):
        for k, listofh in self.__handlers.items():
            if not match_scope(pattern, k):
                continue

            for func in listofh:
                func(ctx, state)

    def __parse_vars(self, key, args, ctx: ZutoCtxI):

        cmdobj = self.cmds[key]
        func = cmdobj.func

        if isinstance(args, str):
            args = resolve_special_var(args, ctx.env)

        # parse the cases if the function uses less than 2 variables (including ctx)
        psig = inspect.signature(func).parameters
        if len(psig) == 0:
            return {}

        params = {}
        for p in psig:
            if p in self.__props:
                params[p] = (
                    self.__props[p](ctx)
                    if "ctx" in inspect.signature(func).parameters
                    else self.__props[p]()
                )

        if (
            not isinstance(args, dict) and 
            ((len(psig) == 2 and "ctx" in psig) 
            or (len(psig) == 1 and "ctx" not in psig))
        ):
            for p in inspect.signature(func).parameters:
                if p != "ctx":
                    params[p] = args

            return params

        #
        if isinstance(args, dict):
            params.update(args)
        elif isinstance(args, list):
            params.update(inspect.signature(func).bind_partial(*args).arguments)
        elif isinstance(args, str):
            listD = args.split(" ")
            params.update(inspect.signature(func).bind_partial(*listD).arguments)

        return params

    def invokeCmd(
        self,
        ctx: ZutoCtxI,
        cmd: str,
        args: dict | list | str,
        pathMatter: str = None,
        invokeChild: bool = True,
    ):
        if cmd not in self.__cmds:
            return args

        if cmd =="exec":
            pass

        cmdobj: ZutoCmd = self.__cmds[cmd]

        if pathMatter and cmdobj.scope:
            if not match_scope(cmdobj.scope, pathMatter):
                return args
        
        params = self.__parse_vars(cmd, args, ctx)

        psig =inspect.signature(cmdobj.func).parameters
        # bind children
        unfilled = list([k for k, v in psig.items() if v.default == inspect.Parameter.empty])
        newparams = {}
        for k, v in params.items():

            if isinstance(v, str):
                newparams[k] = resolve_special_var(v, ctx.env)

            hasCmd = ctx.hasCmd(k)
            childInvokable = isinstance(v, dict) and len(v) == 1 and invokeChild
            if not hasCmd and not childInvokable:
                newparams[k] = v
                if k in unfilled:
                    unfilled.remove(k)
                continue

            if hasCmd:
                result = ctx.runner.run({k: v})
                
            else:
                # check if the key is a cmd
                k2 = list(v.keys())[0]
                if not ctx.hasCmd(k2):
                    continue
                result = ctx.runner.run(v)
            
            if not result:
                continue

            if k not in unfilled and len(unfilled) == 1:
                newparams[unfilled[0]] = result
                unfilled.remove(unfilled[0])
            else:
                newparams[k] = result
                unfilled.remove(k)
        
        # check ctx required
        if "ctx" in psig:
            newparams["ctx"] = ctx
            unfilled.remove("ctx")
        
        if cmdobj.resolve_strings:
            newparams = resolve_auto(newparams, ctx.env)


        # filter
        newparams = {k : v for k, v in newparams.items() if k in psig}
        assert len(unfilled) == 0, f"Unfilled params: {unfilled}"

        return cmdobj.func(**newparams)
