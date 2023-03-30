# quafu_runtime_demo

## How to run simpletest

1. `TestUpload`
```
metadata = {"name": "<specify the name here>", "backend": "testbackend"}

```

2. `TestRun`

```
job = service.run(program_id="<Specify the program_id (the output of 1)>", ...)
```
