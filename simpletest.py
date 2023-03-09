import os
from clients.account import Account
from quafu_runtime_service import RuntimeService

class TestAPI():
    @staticmethod
    def TestUpload():
        account = Account("testapitoken")
        service = RuntimeService(account)
        metadata = {"name": "testname", "backend": "testbackend"}
        service.upload_program(data='program/hello.py', metadata=metadata)

if __name__ == '__main__':
    print(os.getcwd())
    TestAPI.TestUpload()