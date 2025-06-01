"""
This is the main file for the backend of the application.
It is responsible for starting the FastAPI server and for handling the API requests.
"""
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import router


app = FastAPI()
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)

