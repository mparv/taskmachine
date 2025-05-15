from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

from mem_db.in_mem_db import CouchDriver

app = FastAPI()
cd = CouchDriver()

# Serve static files from 'public' folder
app.mount("/static", StaticFiles(directory="public"), name="static")

# Set up Jinja2 templates from 'templates' folder
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/article")
async def get_articles():
    _, articles = await cd.all_docs('article')
    articles = [art['doc'] for art in articles['rows']]
    return {"articles": articles}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7000)
