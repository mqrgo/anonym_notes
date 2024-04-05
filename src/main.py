from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from crud import add_note_into_db, get_note_from_db


app = FastAPI()
templates = Jinja2Templates(directory='templates')
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get('/')
async def root(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.post('/add_note')
async def add_note(request: Request, res = Depends(add_note_into_db)):
    message = 'Your note was sended' if res is True else 'Something was wrong'
    
    return templates.TemplateResponse('message.html', {'request': request, 'message': message})


@app.post('/check_note')
async def check_note(request: Request, res = Depends(get_note_from_db)):
    message = 'Invalid key or id. Prbbly message alredy delete' if res is False else res
    
    return templates.TemplateResponse('message.html', {'request': request, 'message': message})
