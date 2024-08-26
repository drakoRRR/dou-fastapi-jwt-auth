import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from src.config import DEBUG
from src.auth.routers import auth_router


load_dotenv()


def create_app():
    fast_api_app = FastAPI(
        debug=bool(DEBUG),
        docs_url="/api/docs/",
    )

    fast_api_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return fast_api_app


fastapi_app = create_app()

main_api_router = APIRouter()
fastapi_app.include_router(auth_router, prefix="/auth", tags=["Auth"])
fastapi_app.include_router(main_api_router)


if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="0.0.0.0", port=5000)