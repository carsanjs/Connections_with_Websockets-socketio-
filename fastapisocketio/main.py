from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi_socketio import SocketManager

# se inizialized la aplicaction
app = FastAPI()

# agregando seguridad
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# monstamos la aplicaction una ruta
# app.mount("/static", StaticFiles(directory="static"), name="static")

# inicializamos el servidor de la libreria fastapi_socketio,ademas agregamos la "application" de fastapi
sio = SocketManager(
    app=app,
    mount_location="/ws",
    socketio_path="socket.io",
    async_mode="asgi",
    cors_allowed_origins="*",
)


# Manejar el evento "disconnect"
@sio.on("connect")
async def handle_connect(sid, *args, **kwargs):
    print("Connected to client", {"sid": sid})
    await sio.emit("my_response", {"data": "Connected to Server"}, room=sid)


# Manejar el evento "disconnect"
@sio.on("disconnect")
async def handle_disconnect(sid, *args, **kwargs):
    print("Disconnected from client")
    await sio.emit("my_response", "disconnect_message", room=sid)
    sio.disconnect()


# Manejar el evento "my_event"
@sio.on("my_event")
async def handle_my_event(sid, data: dict, *args, **kwargs):
    print("Received messageS:", data)
    await sio.emit("my_response", {"data": data["data"]}, room=sid)

@sio.on("my_broadcast_event")
async def broadcast_event(sid, data):
    await sio.emit(
        "my_response", {"data": data["data"], "room": data["room"]}, room=sid
    )


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    ipclient = request.client.host
    print("ip -->", ipclient)
    with open("static/index.html", "r") as file:
        content = file.read()
    return content
