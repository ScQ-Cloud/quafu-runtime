import os
from clients.account import Account
from quafu_runtime_service import RuntimeService

class TestAPI():
    @staticmethod
    def TestUpload():
        account = Account("testapitoken")
        service = RuntimeService(account)
        metadata = {"name": "testname", "backend": "testbackend"}
        program_id = service.upload_program(data='program/hello.py', metadata=metadata)
        print(program_id)
    @staticmethod
    def TestRun():
        account = Account("testapitoken")
        service = RuntimeService(account)
        job = service.run(program_id="00a03c4bae074119a6dcee6f7e725c15", backend="py_simu", inputs= "zsl")
        print(job.job_id())

if __name__ == '__main__':
    print(os.getcwd())
    TestAPI.TestRun()