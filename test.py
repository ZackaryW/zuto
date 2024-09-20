

from zuto import ext


z = ext()
z.run(
    [
    "test.json",
    {
        "sleep" : 20,
        "ldquit" : {
            "all" : True
        }
    }
    ]
)