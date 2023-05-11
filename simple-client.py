import json

import websocket


def on_open(wsa: websocket.WebSocketApp):
    print('Connected!')
    # wsa.send('From Client')


def on_message(wsa: websocket.WebSocketApp, msg):
    print(f'get msg: {json.loads(msg)}')
    # wsa.send("From client".encode('utf8'))
    # wsa.send('From Client')


def on_close(wsa: websocket.WebSocketApp, status_code, msg):
    print(f'Disconnect!,status_code: {status_code}, msg: {json.loads(msg)}')
    # wsa.send('Close')


def on_error(wsa, error):
    print(error)


if __name__ == '__main__':
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url='ws://127.0.0.1:8765/', on_open=on_open, on_message=on_message, on_close=on_close, on_error=on_error)
    ws.run_forever(ping_interval=60, ping_timeout=10)


# import sys
# import socketio
# import asyncio
# import signal
#
# sio = socketio.AsyncClient()


# def quit(signum, frame):
#     print("quit")
#     sys.exit()
#
#
# @sio.event()
# async def connect():
#     print('Connect!')
#     await sio.emit('message', {'data': 'from connect'})
#
#
# @sio.event
# async def message(data):
#     print(f"msg: {data}")
#     # await sio.sleep(1)
#     # await sio.emit('message', {'data': 'from client'})
#
#
# @sio.event
# async def disconnect():
#     print('Disconnect!')
#     await sio.disconnect()
#
#
# async def main():
#     await sio.connect('ws://127.0.0.1:5000/')
#     await sio.wait()
#
#
# if __name__ == '__main__':
#     signal.signal(signal.SIGINT, quit)
#     signal.signal(signal.SIGTERM, quit)
#     asyncio.run(main())
