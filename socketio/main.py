from fastapi import FastAPI
from fastapi.responses import FileResponse
import socketio
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

HTML_FILE = "./index.html"

# se inicializa la aplicacion con fastapi
app = FastAPI()

# app.mount('/static', app)
# Configuración CORS para permitir solicitudes desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# servidor asincrono con socketio
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*" )
print("servidro socketio", sio)
app.mount("/ws", socketio.ASGIApp(sio, app, socketio_path="/socket.io/"))

background_task_started = False
async def background_task():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        await sio.sleep(10)
        count += 1
        await sio.emit("my_response", {"data": "Hello, world!. Welcome a python socket io"})

@sio.on("connect")
async def test_connect(sid, environ):
    global background_task_started
    if not background_task_started:
        sio.start_background_task(background_task)
        background_task_started = True
        count:int = 0
        count += 1
        print("count", count )
    await sio.emit("my_response", {"data": "Connected", "count": 0}, room=sid)

@sio.on("close room")
async def close(sid, message):
    await sio.emit(
        "my_response",
        {"data": "Room " + message["room"] + " is closing."},
        room=message["room"],
    )
    await sio.close_room(message["room"])


@sio.on("my_room_event")
async def send_room_message(sid, message):
    await sio.emit("my_response", {"data": message["data"]}, room=sid)

#  room=message["room"]

@sio.on("my_event")
async def myevent(sid, message):
    await sio.emit("my_response", {"data": message["data"]}, room=sid)

@sio.on("my_broadcast_event")
async def broadcast_event(sid, message):
    await sio.emit("my_response", {"data": message["data"],
                                   "room": message["room"] 
                                   }, room=sid)

@sio.on("disconnect request")
async def disconnect_request(sid):
    await sio.disconnect(sid)

@sio.on("disconnect")
def test_disconnect(sid):
    print("Client disconnected")


@app.get("/")
async def read_root():
    return FileResponse(HTML_FILE)


# if __name__ == '__main__':
#     uvicorn.run(combined_asgi_app, host='localhost', port=7000)