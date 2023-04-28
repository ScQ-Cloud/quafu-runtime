# import asyncio
# import json
# import time
#
# from flask import Flask
# from flask_socketio import SocketIO, send, emit
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
# # socketio = SocketIO(app, cors_allowed_origins='*')
# name_spec = '/ws'
# socketio = SocketIO()
# socketio.init_app(app, cors_allowed_origins='*')
#
#
# @app.route('/hello')
# def hello():
#     return "hello world"
#
#
# # conncet must send as fast as we can, or client connect will error?
# @socketio.on('connect')
# def handle_connect():
#     print('Connect!')
#     send({'data': 'From Server'})
#     # await asyncio.sleep(1)
#     send({'data': 'code it'})
#
#
# @socketio.on('message')
# def handle_message(msg):
#     print(f'Received message: {msg}')
#     # time.sleep(1)
#     time.sleep(60)
#     send('From server and generate a code')
#     # send('From server')
#
#
# @socketio.on('disconnect')
# def handle_disconnect():
#     print('Disconnect!')
#
#
# @socketio.on_error()
# def handle_error(e):
#     print(f'Something wrong:{str(e)}')
#
#
# if __name__ == '__main__':
#     socketio.run(app)
#
# Websockets
import json
import time

import websockets
import asyncio
from websockets.server import serve

async def handler(websocket):
    print("Connect")
    # 1. check auth
    # 2. check job status
    # 3. create queue and handler interim result
    # await asyncio.sleep(20)
    await websocket.send(json.dumps({'I': 'an'}))
    await handle_get(websocket)
    # 4. delete queue
    print("disconnect")


async def handle_get(websocket):
    while True:
        try:
            # Here should be blocked to get result from broker.
            message = 'From server'
            await asyncio.sleep(100)
            await websocket.send(json.dumps(message))
        except websockets.ConnectionClosed as e:
            break
        except Exception as e:
            print(f'exception: {str(e)}')
            break


async def main_logic():
    async with serve(handler, "localhost", 8765, ping_timeout=10, ping_interval=60):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main_logic())
