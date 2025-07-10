import fastapi
import uvicorn 
from fastapi import FastAPI
import redis.asyncio as redis
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
from house_app.admin.setup import setup_admin
from house_app.db.database import SessionLocal 
from house_app.api.endpoints import auth, predict, social_auth
from starlette.middleware.sessions import SessionMiddleware




async def init_redis():
    return redis.Redis.from_url("redis://localhost", encoding='utf-8', decode_responses=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await init_redis()
    await FastAPILimiter.init(redis)
    yield
    await redis.aclose()


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

house_app = fastapi.FastAPI(title='House.kg', lifespan=lifespan)
house_app.add_middleware(SessionMiddleware, secret_key='SECRET_KEY')
setup_admin(house_app)

house_app.include_router(auth.auth_router)
house_app.include_router(predict.predict_router)
house_app.include_router(social_auth.social_auth_router)


if __name__ == '__main__':
    uvicorn.run(house_app, host='127.0.0.1', port=8080)
