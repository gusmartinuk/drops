from fastapi import FastAPI, Request, Depends, HTTPException, status, security, BackgroundTasks
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import pymysql.cursors
import bcrypt
from settings import *

app = FastAPI()

templates = Jinja2Templates(directory="templates")  # <--- add this line
app.mount("/static", StaticFiles(directory="static"), name="static")

security = HTTPBasic()


from customer_menu import * 
from admin_menu import * 

# Define get_current_user function
def get_current_user(request: Request, email: str = None):
    global connection
    connect()
    if not email:
        email = request.cookies.get('email')    
    if not email:
        disconnect()
        return None
    with connection.cursor() as cursor:
        sql = "SELECT * FROM users WHERE email=%s"
        cursor.execute(sql, (email,))
        result = cursor.fetchone()
        if result:
            disconnect()
            return email
        else:
            disconnect()
            return None


@app.get('/', response_class=HTMLResponse)
async def home(request: Request):    
    return templates.TemplateResponse('home.html', {'request': request})


# Route for login page
@app.get('/login', response_class=HTMLResponse)
async def login(request: Request):    
    return templates.TemplateResponse('login.html', {'request': request})

# Route for handling logout requests
@app.get('/logout')
async def do_logout(request: Request):
    response = RedirectResponse(url='/login')
    response.delete_cookie('email')
    response.delete_cookie('role')
    return response

# Route for handling login requests
@app.post('/login')
async def do_login(request: Request):
    global connection
    connect()
    form = await request.form()
    email = form.get('email')
    password = form.get('password')
    with connection.cursor() as cursor:
        sql = "SELECT * FROM users WHERE email=%s limit 0,1 "
        cursor.execute(sql, (email))
        result = cursor.fetchone()        
        if result:
            hashed_password = result['hashed_password'].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
               role='customer'
               if result['role_id']==555:
                  role='support'  
               elif result['role_id']==999:   
                  role='admin'
               response = RedirectResponse(url='/dashboard_'+role)
               response.set_cookie(key='email', value=email)                
               response.set_cookie(key='role', value=role)                
               disconnect()
               return response
        disconnect()    
        return templates.TemplateResponse('login.html', {'request': request, 'error': 'Incorrect email or password'})

@app.get('/register', response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse('register.html', {'request': request})

@app.post('/register')
async def do_register(request: Request):
    global connection
    connect()
    form = await request.form()
    email = form.get('email')
    password = form.get('password')
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())    
    with connection.cursor() as cursor:
        sql = "SELECT * FROM users WHERE email=%s"
        cursor.execute(sql, (email,))
        result = cursor.fetchone()
        if result:
            disconnect()
            return templates.TemplateResponse('register.html', {'request': request, 'error': 'email already taken'})
        else:
            sql = "INSERT INTO users (email, hashed_password,role_id) VALUES (%s, %s,999)"
            cursor.execute(sql, (email, hashed_password))
            disconnect()
            return RedirectResponse(url='/login')


@app.route('/dashboard_support', methods=['GET', 'POST'])
async def dashboard_support(request: Request):
    email = request.cookies.get('email')
    role = request.cookies.get('role')
    if not email:
        return RedirectResponse(url='/login')
    if role != 'support':
        return PlainTextResponse('Access denied', status_code=403)
    return templates.TemplateResponse('dashboard_support.html', {'request': request, 'email': email, 'role': role})


# Run the app
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
