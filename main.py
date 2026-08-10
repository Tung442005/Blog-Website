from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

#The created object to define all of the routes
app = FastAPI()

#import static files (Contain boostrap elements) and mount the directory 

app.mount("/static", StaticFiles(directory="static"), name="static")

#Create template directory in the project(go to template)
#Tell the APIs where the template is 
templates = Jinja2Templates(directory="templates")

#create request object for Jinja2 template 


posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This frame work is very easy to use",  
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI make it even better",
        "date_posted": "April 21, 2025",
    },
] 

#Representation route
#Home route to response the get request at the root URL
#dont want to include the html class in the FastAPI docs --> use include_in_schema=False
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name='posts')
#the request parameter is the FastAPI mechanism for the route function access to the raw incoming http request object
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {"posts": posts, "title": "Home"})

#Data/backedn route 
# Route to respond to GET requests from the client at /api/posts
# Note: FastAPI treach each @app.get() route as its own islolated handler 
@app.get("/api/posts")
def get_posts():
    # FastAPI automatically converts the list of dicts to JSON
    return posts


@app.get("/api/posts/{post_id}")
def get_posts(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post was not found")
