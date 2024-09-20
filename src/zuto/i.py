class ZutoRunnerI:
    ctx: "ZutoCtxI"

    def addGroup(self, group):
        pass

    def run(self, instruction: dict):
        pass


class ZutoCtxI:

    def hasCmd(self, cmd: str) -> bool:
        pass

    @property
    def metakey(self) -> str:
        pass

    @property
    def meta(self) -> dict:
        pass

    @property
    def metaDepth(self) -> int:
        pass

    @property
    def env(self) -> dict:
        pass

    @property
    def currentStep(self) -> str:
        pass

    @property
    def runner(self) -> "ZutoRunnerI":
        pass

    def setStep(self, step: str):
        pass

    def popStep(self):
        pass

    def getMeta(self, *args):
        pass

    def invokeCmd(self, cmd: str, args: dict | list | str, invokeChild: bool = True):
        pass

    def invokeSignal(
        self,
        name: str,
    ):
        pass

    def invokeHandler(self, pattern: str, state: str):
        pass
