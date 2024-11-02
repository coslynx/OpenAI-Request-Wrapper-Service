from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import jwt
from .routers import request_router, user_router
from .config import settings
from .utils.db import engine, SessionLocal, get_db
from .utils.auth import create_access_token, get_current_user, oauth2_scheme
from .utils.openai import openai_request
from prometheus_client import Counter, start_http_server, Gauge, Histogram

app = FastAPI(
    title="AI Powered OpenAI Request Wrapper Service",
    description="A Python API for simplifying OpenAI requests",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redocs"
)

# Set up CORS middleware for cross-origin requests
origins = ["*"]  # Replace with your actual allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics setup
REQUEST_COUNT = Counter("requests_total", "Total number of requests")
REQUEST_LATENCY = Histogram(
    "request_latency_seconds", "Request latency in seconds"
)

# Prometheus endpoint for scraping metrics
start_http_server(9100)

@app.on_event("startup")
async def startup_event():
    print("Startup event")
    REQUEST_COUNT.inc()

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutdown event")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.include_router(user_router)
app.include_router(request_router)

@app.get("/")
async def root():
    return JSONResponse({"message": "Welcome to the OpenAI Request Wrapper Service!"})

@app.get("/health")
async def healthcheck():
    return JSONResponse({"status": "OK"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)