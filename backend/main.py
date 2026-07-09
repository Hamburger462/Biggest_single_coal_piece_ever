from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "The server is currently up and running"}