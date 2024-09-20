from .runner import ZutoRunner


def default():
    from dotenv import load_dotenv
    load_dotenv()
    runner = ZutoRunner()
    from .groups.builtin import builtin

    runner.addGroup(builtin)
    return runner


def ext():
    runner = default()
    from .groups.ext import ext

    runner.addGroup(ext)
    return runner
