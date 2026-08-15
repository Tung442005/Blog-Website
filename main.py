from typing import Annotated

from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from sqlalchemy import select
from sqlalchemy.orm import Session

#import model
import model
from database import Base, engine, get_db
#No need to import the base class when importing schema
from schemas import PostCreate, PostUpdate, PostResponse, UserCreate, UserResponse, UserUpdate


#Create database table using idempotent
Base.metadata.create_all(bind=engine)


#The created object to define all of the routes
app = FastAPI()

#import static files (Contain boostrap elements) and mount the directory 
#create /static URL prefix and make server serve files from that directory
app.mount("/static", StaticFiles(directory="static"), name="static")

#create /media URL prefix and make server serve files from that directory
app.mount("/media", StaticFiles(directory="media"), name="media")

#Create template directory in the project(go to template)
#Tell the APIs where the template is 
templates = Jinja2Templates(directory="templates")

#create request object for Jinja2 template 


#-------------------------HTML return route----------------------------- 
#Home route to response HTML display to the get request at the root URL
#dont want to include the html class in the FastAPI docs --> use include_in_schema=False
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name='posts')
# #the request parameter is the FastAPI mechanism for the route function access to the raw incoming http request object

#Update the home route(return all posts) with the database included 
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(model.Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"}
    )


#Individual Post Route to repoinse HTML display
@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(model.Post).where(model.Post.id == post_id))
    post = result.scalars().first()
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {"post": post, "title": title}
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")



#Route to return the posts from specific user in HTML
@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts_page")
def user_posts_page(request: Request, user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(model.User).where(model.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    result = db.execute(select(model.Post).where(model.Post.user_id == user_id))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )


#-------------------------Data/backend route----------------------------- 

# Note: FastAPI treach each @app.get() route as its own islolated handler 
#reponse_model will validate each post has all the fields we defined 

#------------------USER------------------------

#Route to response to CREATE requet creating new user
@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(user: UserCreate, db :Annotated[Session, Depends(get_db) ]):
    #check if a username already exist when we create a new user

    #Build and runs a SQL query to check where username exist
    result = db.execute(select(model.User).where(model.User.username == user.username))

    #check matching user was found within the server using the result query above and get the first user_object if it exist
    #scalars() is used to turn each rows in tuple-like containers returned from db.execute to Scalar result(single enity) which help us get plain User objects directly
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )


    #Build and runs a SQL query to check where user email  exist
    result = db.execute(select(model.User).where(model.User.email == user.email))

    #check matching user was found within the server using the result query above and get the first user_object if it exist
    #scalars() is used to turn each rows in tuple-like containers returned from db.execute to Scalar result(single enity) which help us get plain User objects directly
    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    #If non of the above exist --> None --> We gonan
    new_user = model.User(
        username=user.username,
        email=user.email,
    )
    #stages the insert
    db.add(new_user)

    #Execute and save to the database
    db.commit()

    #reload the object from the database 
    db.refresh(new_user)

    #return new_user and Pydantic will automatically convert that to a user response like what we setup with response model
    return new_user


#Route to response GET request specific/individual user 
@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):

    #Build and runs a SQL query to check where user_id exist
    result = db.execute(select(model.User).where(model.User.id == user_id))

    #get the first user object from the database if there exist an user else raise 404 Error
    user = result.scalars().first()

    if user:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


#Route/endpoints to response to the UPDATE request for single posts

@app.patch("/api/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(model.User).where(model.User.id == user_id))
    user = result.scalars().first()
    #check if the user exist to update else return 404 status
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    #check if the updated username the same as current username 
    #if different, check if there is other same username as updated one in database
    if user_update.username is not None and user_update.username != user.username:
        result = db.execute(select(model.User).where(model.User.username == user_update.username))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    if user_update.email is not None and user_update.email != user.email:
        result = db.execute(
            select(model.User).where(model.User.email == user_update.email))
        
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    #UPDATE logic using setattr()
    update_data = user_update.model_dump(exclude_unset=True)

    #loop over Python dict("username": "new_username")
    for field, value in update_data.items():
        #setattr() --> for the user, set field(username) to the value(new_username)
        setattr(user, field, value)


    #UPDATE logic using manual condition statement
    # if user_update.username is not None:
    #     user.username = user_update.username
    # if user_update.email is not None:
    #     user.email = user_update.email
    # if user_update.image_file is not None:
    #     user.image_file = user_update.image_file

    #commit to the database after PUT opereation
    #no need to use db.add() because this is not insertion which require building new object
    db.commit()
    db.refresh(user)
    return user


@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(model.User).where(model.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    db.delete(user)
    db.commit()
    
#------------------POST------------------------

#Route to reponse with the CREATE method 
@app.post("/api/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(model.User).where(model.User.id == post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    new_post = model.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# Route to respond to GET requests from the client at /api/posts
@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(model.Post))
    posts = result.scalars().all()
    # FastAPI automatically serialize the author - post relationship as the user response 
    return posts

#Route response a single post request
@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):

    #Build and runs a SQL query to check where user_id exist
    result = db.execute(select(model.Post).where(model.Post.id == post_id))

    #get the first user object from the database if there exist an user else raise 404 Error
    post = result.scalars().first()

    if post:
        return post 
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


#Route/endpoints to response to the GET request for all the posts by a specific user
@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    #check if the user exist
    result = db.execute(select(model.User).where(model.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    #querry all the posts per user and return them
    result = db.execute(select(model.Post).where(model.Post.user_id== user_id))
    posts = result.scalars().all()
    return posts

#Route/endpoints to response to the UPDATE request for single posts
#PUT --> full update
@app.put("/api/posts/{post_id}", response_model=PostResponse)
def update_post_full(post_id: int, post_data: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(model.Post).where(model.Post.id == post_id))
    post = result.scalars().first()

    #check if the post exist to update --> else 404 error
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post was not found")

    #Check if the client is reassigning the existing post's author,
    #verify the new data contain user_id exists before allowing the update
    if post_data.user_id != post.user_id:
        result = db.execute(select(model.User).where(model.User.id == post_data.user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

    #update all the field in the post 
    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id

    #commit to the database after PUT opereation
    #no need to use db.add() because this is not insertion which require building new object
    db.commit()
    db.refresh(post)
    return post


#PATCH --> partial update
@app.patch("/api/posts/{post_id}", response_model=PostResponse)
def update_post_partial(post_id: int, post_data: PostUpdate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(model.Post).where(model.Post.id == post_id))
    post = result.scalars().first()

    #check if the post exist to update --> else 404 error
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post was not found")

    #No user_id in PostUpdate field --> remove user check 

    #Logic for PATCH --> only update fields that the client actually send 
    #post_data contain the data from the request body
    #model_dump converts a Pydantic model instance back into a plain Python dict
    #exclude_unset = True cancel out the default's client data that pydantic include after update
    #Only include the new data that the client sent in their Json
    update_data = post_data.model_dump(exclude_unset=True)

    #loop over Python dict("title": "new_title")
    for field, value in update_data.items():
        #setattr() --> for that post, set field(title) to the value(new_title)
        setattr(post, field, value)

    #commit to the database after PUT opereation
    #no need to use db.add() because this is not insertion which require building new object
    db.commit()
    db.refresh(post)
    return post

#Route/endpoint to handle DELETE request
@app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(model.Post).where(model.Post.id == post_id))
    post = result.scalars().first()
    #check if the post exist to DELETE --> else 404 error
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post was not found")

    db.delete(post)
    db.commit()

#------------------------Stralette-------------------------------
#Starlette general https exception handler --> custom exception handler
"""
The decorator register the function general_http_exception_handler 
as the handle for any exception that is an instance of StarletteHTTPException
"""


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    #conditional statement to return generic fallback if the the detail is falsy(does not exist within the exception)
    message = (exception.detail if exception.detail else "An error occured. Please chek your request")

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )
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
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
            content = {"detail": exception.errors()}
        )

    return templates.TemplateResponse(
        request, 
        "error.html",
        {"status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
         "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
         "message": "Invalid request. Please check your input and try again"
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
    )

