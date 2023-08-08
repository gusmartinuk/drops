from fastapi import FastAPI, Request, Depends, HTTPException, status, security, BackgroundTasks
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import pymysql.cursors
import bcrypt
from settings import *

from main import app,templates
@app.route('/dashboard_customer', methods=['GET', 'POST'])
async def dashboard_customer(request: Request):
    email = request.cookies.get('email')
    role = request.cookies.get('role')
    if not email:
        return RedirectResponse(url='/login')
    if role != 'customer':
        return PlainTextResponse('Access denied', status_code=403)
    return templates.TemplateResponse('dashboard_customer.html', {'request': request, 'email': email, 'role': role})

@app.route('/customer_search', methods=['GET', 'POST'])
async def dashboard_support(request: Request):
    email = request.cookies.get('email')
    role = request.cookies.get('role')
    if not email:
        return RedirectResponse(url='/login')
    #if role != 'customer':
    #    return PlainTextResponse('Access denied', status_code=403)    
    return templates.TemplateResponse('customer_search.html', {'request': request, 'email': email, 'role': role})
