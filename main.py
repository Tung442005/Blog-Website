from typing import Annotated

from contextlib import asynccontextmanager

from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler

from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.exceptions import RequestValidationError
#Deleted JSONResponse 
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from sqlalchemy import select
# from sqlalchemy.orm import Session
# Change normal Session to Async Session
from sqlalchemy.ext.asyncio import AsyncSession
#import select and load for eager loading relationships
from sqlalchemy.orm import selectinload

#import model
import model
from database import Base, engine, get_db

#import router modules
from routers import posts, users

#No need to import the base class when importing schema
#Delete schema when we use router modules
# from schemas import PostCreate, PostUpdate, PostResponse, UserCreate, UserResponse, UserUpdate


#Create database table using idempotent
# Base.metadata.create_all(bind=engine)
#change from synchronous engine to asynchronous engine using lifespan(used for async)
@asynccontextmanager
async def lifespan(_app: FastAPI):
    #Startup code
    #engine.begin() opens a new AsyncConnection and starts a transaction on it --
    #auto-commits on success, rolls back on error
    async with engine.begin() as conn:
        #run_sync() lets us call the synchronous create_all() from async code,
        #since create_all() has no async-native version
        await conn.run_sync(Base.metadata.create_all)
    #hand control back to FastAPI to start serving requests;
    #execution pauses here until the app shuts down
    yield
    #Shutdown
    await engine.dispose()


#The created app object to define all of the routes for the backend
app = FastAPI(lifespan=lifespan)

#import static files (Contain boostrap elements) and mount the directory 
#create /static URL prefix and make server serve files from that directory
app.mount("/static", StaticFiles(directory="static"), name="static")

#create /media URL prefix and make server serve files from that directory
app.mount("/media", StaticFiles(directory="media"), name="media")

#Create template directory in the project(go to template)
#Tell the APIs where the template is 
#create request object for Jinja2 template 
templates = Jinja2Templates(directory="templates")


#-------------------------Data/backend route----------------------------- 

# Note: FastAPI treach each @app.get() route as its own islolza

#------------------POST------------------------
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])

#------------------USER------------------------
#Include router
app.include_router(users.router, prefix="/api/users", tags=["users"])


#-------------------------HTML return route(Frontend)----------------------------- 
#Home route to response HTML display to the get request at the root URL
#dont want to include the html class in the FastAPI docs --> use include_in_schema=False
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name='posts')
# #the request parameter is the FastAPI mechanism for the route function access to the raw incoming http request object

#Update the home route(return all posts) with the database included 
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(model.Post)
        .options(selectinload(model.Post.author))
    )
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"}
    )


#Individual Post Route to repoinse HTML display
@app.get("/posts/{post_id}", include_in_schema=False)
async def post_page(request: Request, post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(model.Post)
        .options(selectinload(model.Post.author))
        .where(model.Post.id == post_id)
    )
    
    post = result.scalars().first()
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {"post": post, "title": title}
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")



#Route to return the posts from specific user in HTML(User post page)
@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts_page")
async def user_posts_page(request: Request, user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    #does not need selectInload since it does not access relationship (post --> author)
    result = await db.execute(
        select(model.User)
        .where(model.User.id == user_id))
    
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    #need selectInload since it does not access relationship (post --> author)
    result = await db.execute(
        select(model.Post)
        .options(selectinload(model.Post.author))
        .where(model.Post.user_id == user_id))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )





#------------------------Stralette-------------------------------
#Starlette general https exception handler --> custom exception handler
"""
The decorator register the function general_http_exception_handler 
as the handle for any exception that is an instance of StarletteHTTPException
"""


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):


    if request.url.path.startswith("/api"):
        #Starlette's exception-handling machinery expects every registered handler to return a Response object
        return await http_exception_handler(request, exception)

    #conditional statement to return generic fallback if the the detail is falsy(does not exist within the exception)
    message = (exception.detail if exception.detail else "An error occured. Please chek your request")
    
    #if not api route --> return html response
    return templates.TemplateResponse(
        request, 
        "error.html",
        {"status_code": exception.status_code, "title": exception.status_code, "message": message},
        #make sure the reponse code is correct not just 200
        status_code=exception.status_code
    )


#-----------------------Request Validation Error------------------------------
#Value Tpye Validation error (422) --> Request Validation Error not HTTP exception
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)
    
    return templates.TemplateResponse(
        request, 
        "error.html",
        {"status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
         "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
         "message": "Invalid request. Please check your input and try again"
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
    )

