from fastapi import FastAPI, UploadFile, Depends
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from domain.bucketlist import bucketlist_router
from domain.user import user_router
from domain.review import review_router
from dotenv import load_dotenv

from models import Image
from sqlalchemy.orm import Session
from database import get_async_db

import os
import uuid

load_dotenv(override=True)
BE_URL = os.getenv("BE_URL")
FE_URL = os.getenv("FE_URL")

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
app.mount("/image_file", StaticFiles(directory="./image_file"), name="image_files")


@app.post("/image")
async def upload_image(file: UploadFile, db: Session = Depends(get_async_db)):
    UPLOAD_DIR = "./image_file"  # 이미지를 저장할 서버 경로

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    content = await file.read()
    filename = f"{str(uuid.uuid4())}.jpg"  # uuid로 유니크한 파일명으로 변경
    file_path = os.path.join(UPLOAD_DIR, filename)
    file_url = f"{BE_URL}{file_path[1:]}"

    with open(file_path, "wb") as fp:
        fp.write(content)  # 서버 로컬 스토리지에 이미지 저장 (쓰기)

    db_image = Image(data=file_path[1:])
    db.add(db_image)
    await db.commit()

    return {"filename": filename, "file_url": file_url}
