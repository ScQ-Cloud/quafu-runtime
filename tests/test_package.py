from quafu_runtime import RuntimeService
from quafu_runtime import Account

API_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MTI3MiwiZXhwIjoxNjg1MTY0MjM1fQ.BuTKgSuvxjrZcgV8YmmkNScGvdQfrYbHphEMxI9n7p8"
API_TOKEN = API_TOKEN[::-1]

account = Account(api_token=API_TOKEN)
service = RuntimeService(account)
res = service.program(name='long-run-task')
print(res)
