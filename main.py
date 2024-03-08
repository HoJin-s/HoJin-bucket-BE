from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from domain.bucketlist import bucketlist_router
from domain.user import user_router
from domain.review import review_router
from domain.image import image_router
import os
from settings import get_be_url, get_fe_url, get_upload_dir

BE_URL = get_be_url()
FE_URL = get_fe_url()
UPLOAD_DIR = get_upload_dir()

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

# 서버 디렉토리에 대한 StaticFiles 미들웨어 등록
if os.path.exists(UPLOAD_DIR):
    app.mount(
        UPLOAD_DIR[1:], StaticFiles(directory=UPLOAD_DIR), name=f"{UPLOAD_DIR[2:]}s"
    )

# 테스트코드 디렉토리에 대한 StaticFiles 미들웨어 등록
if os.path.exists("./image_file_test"):
    app.mount(
        "/image_file_test",
        StaticFiles(directory="./image_file_test"),
        name="image_files_test",
    )
