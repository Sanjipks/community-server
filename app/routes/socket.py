from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from app.utilityFunctions.security import require_user

  

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, dependencies=Depends(require_user)):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        print("WebSocket disconnected")