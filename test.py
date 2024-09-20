

from zuto import ext


z = ext()
z.run(
    [
    # test single value
    "debug",

    # test complete dict
    {
        "vars" : {
            "test_var" : "${https://gist.githubusercontent.com/sunilshenoy/23a3e7132c27d62599ba741bce13056a/raw/517b07fc382c843dcc7d444046d959a318695245/sample_json.json}"
        },
        "steps" : [
            {   
                "eval" : "ww = test_var['clientIdentiferData']['clientID']",
                "echo" : "${ww}"
            },
            # test nested values
            {"echo" : {"eval" : "ww = int(ww) + 1"}},
        ]
    },

    # test echoing special vars
    {
        "echo" : "${https://gist.githubusercontent.com/gdb/b6365e79be6052e7531e7ba6ea8caf23/raw/1fe04499830ec87e1d3130cc4ce818251fa7c5cf/Sample%2520gist}"
    },
    {
        "os" : "echo helloworld !!!!"
    },
    # test first
    {
        "first" : [
            "${kk.yaml}",
            "${test.json}",
        ]
    },
    {
        "sleep" : 20,
        "ldquit" : {
            "all" : True
        }
    }
    ]
)

while True:
    pass