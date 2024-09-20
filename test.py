

from zuto import ext


z = ext()
z.run(
    [
    {
        "sleep" : 2,
        "exec" : "notepad.exe",
        "ldrun" : {
            "id" : 1
        }
    },
    {
        "sleep" : 20,
        "ldquit" : {
            "all" : True
        }
    }
    ]
)