from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def root():
    return JSONResponse({"message": "Welcome to Recipe Level Predictor API"})

@app.get("/test")
async def test():
    return JSONResponse({"message": "FastAPI is working!"})
