from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from domain.bucketlist import bucketlist_router
from domain.user import user_router
from domain.review import review_router
from domain.image import image_router
from dotenv import load_dotenv

import os

load_dotenv(override=True)
BE_URL = os.getenv("BE_URL")
FE_URL = os.getenv("FE_URL")
UPLOAD_DIR = "./image_file"

app = FastAPI()

origins = [
    FE_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bucketlist_router.router)
app.include_router(user_router.router)
app.include_router(review_router.router)
# 이미지파일 저장
app.include_router(image_router.router)

if os.path.exists(UPLOAD_DIR):
    app.mount("/image_file", StaticFiles(directory="./image_file"), name="image_files")
