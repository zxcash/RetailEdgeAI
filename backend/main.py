from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from datetime import datetime
from threading import Lock
import time

import cv2
import numpy as np
from pydantic import BaseModel, Field


# ============================================================
# RETAILEDGE AI BACKEND
# ============================================================

app = FastAPI(
    title="RetailEdge AI",
    description="AI-powered Edge Retail Intelligence Platform",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# LIVE DATA
# ============================================================

live_data = {
    "current_shoppers": 0,
    "tracking_ids": [],
}


# ============================================================
# DASHBOARD DATA
# ============================================================

dashboard_data = {
    "store": {
        "name": "RetailEdge Demo Store",
        "status": "ONLINE",
    },

    "shopper": {
        "current": 0,
        "entries_today": 128,
        "exits_today": 116,
        "peak": 24,
    },

    "inventory": {
        "total_products": 120,
        "available": 113,
        "low_stock": 5,
        "out_of_stock": 2,
    },

    "queue": {
        "current": 3,
        "average": 2.1,
        "wait_seconds": 7.5,
        "status": "BUSY",
    },

    "zones": {
        "Grocery": 42,
        "Electronics": 31,
        "Pharmacy": 58,
        "Checkout": 25,
    },

    "alerts": [
        {
            "type": "inventory",
            "severity": "warning",
            "message": "Shelf B is running low on stock",
        },
        {
            "type": "queue",
            "severity": "info",
            "message": "Checkout queue is increasing",
        },
    ],

    "last_updated": datetime.now().isoformat(),
}


# ============================================================
# VIDEO FRAME STORAGE
# ============================================================

latest_frame = None
frame_lock = Lock()


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "application": "RetailEdge AI",
        "status": "running",
        "message": "Edge Retail Intelligence API",
    }


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/api/dashboard")
def dashboard():

    dashboard_data["last_updated"] = datetime.now().isoformat()

    return dashboard_data


# ============================================================
# SHOPPER
# ============================================================

@app.get("/api/shopper")
def shopper():

    return dashboard_data["shopper"]


# ============================================================
# INVENTORY
# ============================================================

@app.get("/api/inventory")
def inventory():

    return dashboard_data["inventory"]


# ============================================================
# QUEUE
# ============================================================

@app.get("/api/queue")
def queue():

    return dashboard_data["queue"]


# ============================================================
# ZONES
# ============================================================

@app.get("/api/zones")
def zones():

    return dashboard_data["zones"]


# ============================================================
# ALERTS
# ============================================================

@app.get("/api/alerts")
def alerts():

    return dashboard_data["alerts"]


# ============================================================
# LIVE AI DATA
# ============================================================

class LiveData(BaseModel):

    current_shoppers: int

    tracking_ids: list[int] = Field(
        default_factory=list
    )


@app.post("/api/live")
def update_live(data: LiveData):

    live_data["current_shoppers"] = data.current_shoppers

    live_data["tracking_ids"] = data.tracking_ids

    dashboard_data["shopper"]["current"] = (
        data.current_shoppers
    )

    return {
        "status": "updated",
        "current_shoppers": data.current_shoppers,
        "tracking_ids": data.tracking_ids,
    }


@app.get("/api/live")
def get_live():

    return {
        "current_shoppers": live_data["current_shoppers"],
        "tracking_ids": live_data["tracking_ids"],
    }


# ============================================================
# RECEIVE CAMERA FRAME
#
# IMPORTANT:
# We use Request directly here instead of `frame: bytes`.
# This avoids the 422 body-validation problem.
# ============================================================

@app.post("/api/video/frame")
async def receive_video_frame(request: Request):

    global latest_frame

    try:

        # Read raw JPEG bytes
        body = await request.body()

        if not body:

            return {
                "status": "empty_frame"
            }


        # Convert bytes -> numpy
        array = np.frombuffer(
            body,
            dtype=np.uint8
        )


        # JPEG -> OpenCV frame
        decoded = cv2.imdecode(
            array,
            cv2.IMREAD_COLOR
        )


        if decoded is None:

            return {
                "status": "invalid_jpeg"
            }


        # Store latest frame
        with frame_lock:

            latest_frame = decoded


        return {
            "status": "frame_received",
            "width": int(decoded.shape[1]),
            "height": int(decoded.shape[0]),
        }


    except Exception as e:

        print(
            f"VIDEO FRAME ERROR: {e}"
        )

        return {
            "status": "error",
            "message": str(e),
        }


# ============================================================
# MJPEG GENERATOR
# ============================================================

def generate_video():

    global latest_frame

    while True:

        with frame_lock:

            if latest_frame is not None:

                frame = latest_frame.copy()

            else:

                frame = None


        # ----------------------------------------------------
        # WAITING SCREEN
        # ----------------------------------------------------

        if frame is None:

            frame = np.zeros(
                (720, 1280, 3),
                dtype=np.uint8
            )

            cv2.putText(
                frame,
                "RETAILEDGE AI",
                (455, 300),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (255, 255, 255),
                3,
            )

            cv2.putText(
                frame,
                "Waiting for edge camera...",
                (430, 365),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (170, 170, 170),
                2,
            )


        # ----------------------------------------------------
        # ENCODE JPEG
        # ----------------------------------------------------

        success, encoded = cv2.imencode(
            ".jpg",
            frame,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                85,
            ],
        )


        if success:

            frame_bytes = encoded.tobytes()

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: "
                + str(len(frame_bytes)).encode()
                + b"\r\n\r\n"
                + frame_bytes
                + b"\r\n"
            )


        time.sleep(0.033)


# ============================================================
# LIVE VIDEO STREAM
# ============================================================

@app.get("/api/video")
def video_feed():

    return StreamingResponse(
        generate_video(),
        media_type=(
            "multipart/x-mixed-replace; "
            "boundary=frame"
        ),
        headers={
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )


# ============================================================
# HEALTH
# ============================================================

@app.get("/api/health")
def health():

    with frame_lock:

        camera_connected = (
            latest_frame is not None
        )

    return {
        "status": "healthy",
        "camera_stream": camera_connected,
        "current_shoppers": (
            live_data["current_shoppers"]
        ),
        "timestamp": datetime.now().isoformat(),
    }