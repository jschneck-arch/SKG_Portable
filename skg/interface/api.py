from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()
class Ingest(BaseModel):
    text: str
    tag: str = "note"
@app.get("/health")
def health():
    return {"ok": True}
