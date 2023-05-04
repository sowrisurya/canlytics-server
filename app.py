from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import ROUTES
import os
import uvicorn


app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

for route in ROUTES:
	app.include_router(route, prefix="/api/v1")

@app.get("/")
async def root():
	return {"message": "Hello World"}

@app.get("/health")
async def health_check():
	return {"message": "OK"}

if __name__ == "__main__":
	if os.getenv("ENV") == "prod":
		uvicorn.run("app:app", host="0.0.0.0", port=80, reload=False, workers=4)
	elif os.getenv("ENV", "dev") == "dev":
		uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
