from fastapi import FastAPI, Request, Depends, HTTPException, status, security, BackgroundTasks
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import pymysql.cursors
import bcrypt
from settings import *
from main import app,templates

# Route that requires authentication to access
@app.route('/dashboard_admin', methods=['GET', 'POST'])
async def dashboard_admin(request: Request):
    email = request.cookies.get('email')
    role = request.cookies.get('role')
    if not email:
        return RedirectResponse(url='/login')
    if role != 'admin':
        return PlainTextResponse('Access denied', status_code=403)
    return templates.TemplateResponse('dashboard_admin.html', {'request': request, 'email': email, 'role': role,'message':''})

@app.route('/backup', methods=['GET', 'POST'])
async def dashboard_support(request: Request):
    global connection
    email = request.cookies.get('email')
    role = request.cookies.get('role')
    if not email:
        return RedirectResponse(url='/login')
    if role != 'admin':
        return PlainTextResponse('Access denied', status_code=403)    
    connect()
    import backup
    message=backup.backup_database()
    disconnect()
    return templates.TemplateResponse('dashboard_admin.html', {'request': request, 'email': email, 'role': role,'message':message})

"""
# retired  converted to cronjob vidaxl/vidatoproducts.py
@app.route('/admin_load_vidaxl', methods=['GET', 'POST'])
async def dashboard_support(request: Request):
    email = request.cookies.get('email')
    role = request.cookies.get('role')
    if not email:
        return RedirectResponse(url='/login')
    if role != 'admin':
        return PlainTextResponse('Access denied', status_code=403)
    connect()
    import suppliers.load_vidaxl
    disconnect()
    message=suppliers.load_vidaxl.vidaxl()
    return templates.TemplateResponse('dashboard_admin.html', {'request': request, 'email': email, 'role': role,'message':message})
"""
@app.route('/admin_load_bigbuy', methods=['GET', 'POST'])
async def dashboard_support(request: Request):
    email = request.cookies.get('email')
    role = request.cookies.get('role')
    if not email:
        return RedirectResponse(url='/login')
    if role != 'admin':
        return PlainTextResponse('Access denied', status_code=403)
    connect()
    import suppliers.bigbuy_ftp
    disconnect()
    message=suppliers.bigbuy_ftp.bigbuy()
    return templates.TemplateResponse('dashboard_admin.html', {'request': request, 'email': email, 'role': role,'message':message})
