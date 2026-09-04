## **Part 1: Getting Started: REST API + Web App** 

Following Task to finish:
- Know the difference:
    + API: the overall service/interface that FASTAPI expose which contain sets of routes, request/response formats and rules for how other program interact with
    + Endpoints: one specfic URL path + HTTP method combination within the API
- Install Fast API(standard) 
    + Include the framework API itself
    + Uvcorn: ASGI server to run the application
    + fast API CLI command to run the app
- Build the basics within the application
    + Fast API use decoraters to define route
        * FastAPI use the function name as the route name
        * If both route(@decorator) point to the same function --> need explicit name for each route so it does not point to the same function
    + CLI commnad: 
        * python -m fastapi dev main.py 
            - Include auto reload so whenever we make changes to the code, the server automatically restarted 
            - Give dev more helpful debugging output 
        * python -m fastapi run main.py
            - Does not have auto reload
            - Better for performance optimization --> better to be ran in produciton

    + Curl command: 
        * command-line tool for making HTTP requests 
        * it send request to the endpoints within the python script, asking for the JSON response
        * The server with endpoint handler(@app.get("/")) reponse with the JSON response


- Build a couple of routes that connect to JSON
    + The API route reponse with the JSON data is good for programmatic access for other server or frontend
    + We can display the JSON with HTML using HTMLReponse but not recommend for API docs but rather for human browsing the site

- Run the app from the command line 
- Look at the some automatic documentation
- Get some dummy data and create an API endpoint 
- Create some HTML response from API endpoints


## **Part 2: HTML Frontend for Your API Using Jinja 2 Template** 

- Jinja 2 Template: 
    - What is template engine? 
        - A software tool that combine static layout files with dynnamic data to generate a final docment usually HTML for web pages
        - It replace places holders tag within html file with real data values 
        - This keep presentation design seperate from core programming code
    - It is template engine allow developers to write HTML files and just pass in our dynamic data
    - This solve the problem when FastAPI return JSON which is perfect for API access but not for human
    - Jinja 2 template require the request object because:
        - FastAPI's HTML templating is built on Starlette's Jinja2Templates, which injects a **url_for helper function** into the template's rendering context so you can write things like 
        ```<a href="{{ url_for('get_posts') }}"> ```
        inside your HTML instead of hardcoding /api/posts.

    - Example of usage of Jinja 2 Template:
        * Within the template
            ```.html
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>FastAPI Blog</title>
                </head>
                <body>
                    <h1>Home Page</h1>
                    {% for post in posts %}
                        <h2>{{ post.title }}</h2>
                        <p>{{ post.content }}</p>
                    {% endfor %}
                </body>
            </html>
            ```
        * Within the Fast API server (main.py)
            ```.py
            @app.get("/", include_in_schema=False)
            @app.get("/posts", include_in_schema=False)
            #the request parameter is the FastAPI mechanism for the route function access to the raw incoming http request object
            def home(request: Request):
                return templates.TemplateResponse(request, "home.html", {"posts": posts, "title": "Home"})
            ```
    - Template Inheritance
        * If we want to create more pages such as about page, a single post page, we would have to copy the entire HTML structure to other files
        * If we duplicate it like that and wantd to change the navigation link, then we would have to update that on every single template that just would not be maintainable
        * How to solve: Create a parent template with the common structure so other pages can inherit from it (layout.html)
        * Example:
            * In layout.html file
            ```.html
            <!-- define a section called content that a child template can override -->
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>
                        {% if title %}
                        FastAPI Blog - {{ title }}
                        {% else %}
                        FastAPI Blog
                        {% endif %}
                        
                    </title>
                </head>
                <body>
                    {% block content %}
                    {% endblock content %}
                </body>
            </html>
            ```

            *In home.html file
            ```.html
            <!-- Extend the layout file-->
            {% extends "layout.html" %}
            {% block content %}
                {% for post in posts %}
                    <h2>{{ post.title }}</h2>
                    <p>{{ post.content }}</p>
                {% endfor %}
            {% endblock content %}
            ```

- Styling the web with boostrap framework
    * Within the `main.py `need to import static files and mount the directory, why?
        - With CRUD in Fast API, it only knows to response from the route we define action for it. They only repsonse to a request if it matches somthing registerd in its routing table
        - 
        - By Mounting those static files, we tell the server to serve everything under this folder directly(URL path)
        -  Instead of "here's what to do for exactly this one URL," it's "here's what to do for this whole family of URLs, and let the mounted app figure out the specifics per-request."
        - Example

        ```
        from fastapi.staticfiles import StaticFiles

        app.mount("/static", StaticFiles(directory="static"), name="static")
        ```

        - `app.mount()` delegate URL prefix to seperate ASGI application(Python callable that handle network event detached from other service), rather then define single handler for single path 
        - `"/static"` is the URL path wwhere the static files will be accessible
        - `StaticFiles(directory="static")` — an instance pointing our "static" folder(self-contained ASGI app) whose entire job is: take whatever path comes after the prefix, look for a matching file in the static/ folder on disk, and stream it back as the response (with correct Content-Type, 404 if missing, etc.).
        - `name="static"` — lets you refer to it in templates via url_for('static', path='css/style.css') instead of hardcoding /static/....
    * Within the `layout.html`:
        - use `url_for('static', path='css/style.css')` to properly generate URLs in templates --> two main use cases:
            * For route link navigation
            * For static files like css, javascript and images
        - Benefit use `url_for`:
            * If you ever change your routes or change the mount path --> all the link will be updated



## **Part 3: Path Parameters - Validation and Error Handling** 

- **Path URL paramter -> Create Single Post Endpoint for the API:**
    * Use to grab a single post with individual API endpoint and have view of a specific page
    * Whatever value got passed into the UTR parameter will tell FASTAPI that this is the part of URL and it should be capture as parameter in the our function
    * Example:
    ```.py
    from fastapi import HTTPException, status

    @app.get('/api/posts/{post_id}')
    def get_posts(post_id: int):
        for post in posts:
            if post.get("id") == post_id:
                return post
        raise HTTPException(status=status.HTTP_404_NOT_FOUND, detail="Post was not found")
    ```

- **What is the difference between Startlette and FastAPI?**
    * Startlette: Low-level HTTP tools with following key features
        - sync ready: Built for high-speed, concurrent code using asyncio or trio.
        - Lightweight toolkit: Use it as a full micro-framework or pick individual tools as a toolkit.
        - WebSockets: Full real-time bi-directional socket support.
        - Built-ins: Includes routing, static files, CORS, and background tasks
    * FastAPI:
        - Built on top of Starlette. 
        - It adds automatic data validation, type hints, and interactive API docs
- **Create Single Post for the webpage**
    * Need to create endpoints for both API and HTML responses
    * Need to handle error for both API response(JSON) and HTML display (Error Page)
    * Error Page: Why use both HTTPExceptions from starlette.exceptions and fastapi?
        - Register the exception handler on starlette.exceptions.HTTPException (the base class), not fastapi.HTTPException (the subclass). 
        - Since FastAPI's HTTPException is-a Starlette HTTPException, a handler on the base catches both your manually raised errors and Starlette's own routing-level errors (like 404 for unmatched routes). Registering only on the FastAPI subclass would miss the framework's own errors, since those are raised as plain base-class instances. --> need both
        - Example of register a function to handle any exception that belong to Startlette Exception Baseclass
        ```.py
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
        ```
- **Request Data Type Validation Error**
    * *Validation Error 422 (Unprocessable Content / Entity)* means the server completely understands your request syntax and formatting, but the data inside the request is invalid, incomplete, or violates business logic.
    * 422 Error have a list of details string describing the error information
    * Does not have status_code attribute --> need to specifically define it
    * Example:
    ```.py
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
    ```


## **Part 4: Use Pydantic Schema Response Request & Validation** 

- Create Schema Files with request and response models and update get endpoints to use those models:
    * What is Pydantic?
        - It is a data validation library use Pthon type hints
        - Pydantic enforces them at runtime and give you detailed error messasges when somehting does not match
        - Comes built in with fastAPI
        - Automatically give us API documentation
        - It create API contracts specfying what data comes in and what come out
    * Pydantic Validation Schema:
        - They define what data we accept from client and what data we return 
        - The Database define what data do we store 
    * Response Model:
        - Build response model(`PostResponse, UserResponse`) to our endpoints, which tell FastAPI exactily we are going to return 
        - This allow FastAPI doc to return the exact field, type and validation rules
        - When a raw ORM object is returned from the endpoints, FastAPI will:
            - Validate it against Reponse Models using `from_attrubutes=True` to read them off the object
            - Filter the output to only the declared fields
            - Serializes the result to JSON and documents the exact shape in `/docs`


- Create schemas
    * Pydantic import library:
        * BaseModel: The base class that all of the pydantic models inherit from 
        * Field: let us add constrainst like minimum and maximum length
        * Config dict: Configure models

- Create base schema with fields shared between creating and returning posts
    * It need data type and constrainst condition
    * If there is no default value then the field is the required field
- Add reponse_model to the get route for datavalidation
- Create a post endpoint to add new posts


## **Part 5: Adding Database/Models using SQLAlchemy**

- **Problem statements**:
    * As we use the ``posts`` lists --> it only store the data within the local machine's memory. Therefore, when the server is restarted, the posts list is recreated with the harded-code only 
    * Any posts that we create are going to dissapear
    * Therefore, we need database to persist the data across restarts --> use database
- **What is ORM?**
    * Programming technique that connects object-oriented code to relational databases. It lets developers perform database actions using native programming language objects instead of writing raw SQL queries
- **What to use in this projects?**
    * Use SQL Alchemy library to interact with the database
    * At first, just use SQL lite to build a database --> then move to Postgre SQL with configuration change(connect different URL) with the code staying the same
    * Set up relationship between schemas --> easier to validate

- **Application Architecture:**
    * Database Models: 
        - Store the data
        - Contain ORM sepcific features like relationship
    * Pydantics Schema: Data Validation
        - Define API contract
    * API route: API endpoints handle the actual request

-  **Why using seperate models instead of just one combination?**
    * Better controls
    * Better for learning purpose
    * Industry stanard

- **Full process(Overall Picture):**
    * RequestS sent to the endpontS
    * Pydantic Validate it 
    * SQL stores or retrieves the data
    * Pydantic formats the response --> The response goes out 

- **Create Database:**
    * `DATABASE_URL` tell the SQL Alchemy where to connect for SQL lite, blog.db is created automattically
    * `Engine` variable is the object control & manage connection pool to the database 
        - `"check_same_thread":Fasle` is SQLite specific since SQL light normally only allows one thread but FastAPI handles multiple request across thread --> need to disable it
    * `SessionLocal` is the factory that creates database sessions --> the sessions si basically a transaction with the database  --> Each request gets its own sessison
        - This is waht you actually use to query/insert/update
        - Set `autocommit= False` and `autoflush=False` because we want to control when changes are commited --> standard FastAPI implementation
    * `class Base(DeclarativeBase)`:used for sharing parent class for future ORM models --> inheriting from Base is what lets SQLAlchemy discover and map Class object to an actual table name in db (and lets Base.metadata.create_all(engine) generate that table in blog.db).
    * `get_db()` is a dependency function that provide sessions to our route(geneator using yield)
        - `With` statement make the session work as a context manager --> ensure clean up if error occur
    * Dependency injection: software pattern 


- **Create Database Models: Define our database tables using SQL Alchemy OM**
    * UTC is the new Python datetime library
    * `mapped` and `mapped_column` is the declarative mappign tool --> define database table by using Python type hint(formal annotation specifying the expected data types of variable, func para, returned values)
    * the `Mapped[...]` annotation says what Python type, `mapped_column(...)` says how it behaves as a column: primary key, nullable, unique, foreign key, default value, explicit SQL type override, etc.
    * `index = True`: Search the row by id --> faster then scanning the whole db

- **Upadate the Pydantic Schema such that it can work with the defined database models**
    * Author in the "in-memory" posts list is just a string. But now, we have updated with user models --> need to update the pydantic schema to work with it
    * Need to update the schemas into private and public because we dont want the `UserReponse(UserBase)` inherit from the UserBase schema and return private information
    * When SQL ALchemy loads a post, it can also load the related users --> Pydantic see the `author: UserReponse` field, abd valudate user object agaisnt UserReposnse and includes the full user data in our API response. The UserReponse here act as the data type making sure the author field should contain full object shape like UserReponse not just raw value
        - Full process:
            * Querry a ``post`` from database 
            * FastAPI serializes that `post` using `response_model = PostResponse`:
                * Read each field and reach `post.author` -- gets a `User` object
                * Since the schema says `author: UserResponse`, Pydantic recursiely validate that User object against UserReposnse's rule
                * After validate, the final JSON response embed the whole user object as:
                ```.json
                {
                    "id": 1,
                    "title": "FastAPI is Awesome",
                    "content": "...",
                    "user_id": 3,
                    "date_posted": "2026-08-14T10:00:00Z",
                    "author": {
                        "id": 3,
                        "username": "jane",
                        "email": "jane@x.com",
                        "image_file": null,
                        "image_path": "/static/profile_pics/default.jpg"
                    }
                }

                ```
- **Upadate the `main.py` to make the request functional with the Pydantic Schema and Database Models**
    * Include database support modules:
        ```.py
        from fastapi import FastAPI, Request, HTTPException, status, Depends
        from typing import Annotated
        from sqlalchemy import select
        from sqlalchemy.orm import Session
        import model
        from database import Base, engine, get_db

        ```
        - `Annotated`: lets you attach extra metadata to a typehint without chaning what the type actually is. With FastAPI, it will attach dependency injection or valiation metadata directly onto a prameter's type hint 
        - `Depends`: Dependency Injection --> it is how we will inject the database session into our route
        - `select`: querrying styling of sqlalchemy version 
        - `Session`: it is for the IDE knows what type of DB paramter 
        - `models`: Give us access to our post and user models that we just created
        - `Base` and `engine`: Used to create tables
        - `get_db`: it is the dependcy function that provide database sessions
    * Create database table before we even start the app:
    
            ```.py
            Base.metadata.create_all(bind=engine)
            ```
            - `Base.metadata` is the registry object holding the full schema defintiion of every model that;s ever inherited from Base --> it is the SQL Alchemy's in-memory blueprint of all tables, columns, types and constrainst
            - `.create_all(bind=enigne)` wals through everything registered in `Base.metadata` and generate table corresponding to `CREATE TABLE` statement in SQL 
    * Mount the media directory for user uploaded content:
        ```
        app.mount("/media", StaticFiles(directory="media"), name="media")
        ```
    * Update `@app.post` and `@app.get` of both User and Post 
        - Using the database passing to the function paramter of both user and post table
        - This tell FastAPI that before running the CRUD function, call `get_db` and pass the result as the db parameter here --> basically give session when user request and clean the session when the request finished
        ```.py
                ## database.py
        from sqlalchemy import create_engine
        from sqlalchemy.orm import DeclarativeBase, sessionmaker

        SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False},
        )

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


        class Base(DeclarativeBase):
            pass


        def get_db():
            with SessionLocal() as db:
                yield db


        ## models.py
        from __future__ import annotations

        from datetime import UTC, datetime

        from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
        from sqlalchemy.orm import Mapped, mapped_column, relationship

        from database import Base


        class User(Base):
            __tablename__ = "users"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
            email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
            image_file: Mapped[str | None] = mapped_column(
                String(200),
                nullable=True,
                default=None,
            )

            posts: Mapped[list[Post]] = relationship(back_populates="author")

            @property
            def image_path(self) -> str:
                if self.image_file:
                    return f"/media/profile_pics/{self.image_file}"
                return "/static/profile_pics/default.jpg"


        class Post(Base):
            __tablename__ = "posts"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            title: Mapped[str] = mapped_column(String(100), nullable=False)
            content: Mapped[str] = mapped_column(Text, nullable=False)
            user_id: Mapped[int] = mapped_column(
                ForeignKey("users.id"),
                nullable=False,
                index=True,
            )
            date_posted: Mapped[datetime] = mapped_column(
                DateTime(timezone=True),
                default=lambda: datetime.now(UTC),
            )

            author: Mapped[User] = relationship(back_populates="posts")


        ## get_user_posts
        @app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
        def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
            result = db.execute(select(models.User).where(models.User.id == user_id))
            user = result.scalars().first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
            posts = result.scalars().all()
            return posts


        ## home
        @app.get("/", include_in_schema=False, name="home")
        @app.get("/posts", include_in_schema=False, name="posts")
        def home(request: Request, db: Annotated[Session, Depends(get_db)]):
            result = db.execute(select(models.Post))
            posts = result.scalars().all()
            return templates.TemplateResponse(
                request,
                "home.html",
                {"posts": posts, "title": "Home"},
            )


        ## post_page
        @app.get("/posts/{post_id}", include_in_schema=False)
        def post_page(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
            result = db.execute(select(models.Post).where(models.Post.id == post_id))
            post = result.scalars().first()
            if post:
                title = post.title[:50]
                return templates.TemplateResponse(
                    request,
                    "post.html",
                    {"post": post, "title": title},
                )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


        ## user_posts_page
        @app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
        def user_posts_page(
            request: Request,
            user_id: int,
            db: Annotated[Session, Depends(get_db)],
        ):
            result = db.execute(select(models.User).where(models.User.id == user_id))
            user = result.scalars().first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
            posts = result.scalars().all()
            return templates.TemplateResponse(
                request,
                "user_posts.html",
                {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
            )


        ## get_posts
        @app.get("/api/posts", response_model=list[PostResponse])
        def get_posts(db: Annotated[Session, Depends(get_db)]):
            result = db.execute(select(models.Post))
            posts = result.scalars().all()
            return posts


        ## create_post
        @app.post(
            "/api/posts",
            response_model=PostResponse,
            status_code=status.HTTP_201_CREATED,
        )
        def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
            result = db.execute(select(models.User).where(models.User.id == post.user_id))
            user = result.scalars().first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            new_post = models.Post(
                title=post.title,
                content=post.content,
                user_id=post.user_id,
            )
            db.add(new_post)
            db.commit()
            db.refresh(new_post)
            return new_post


        ## get_post
        @app.get("/api/posts/{post_id}", response_model=PostResponse)
        def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
            result = db.execute(select(models.Post).where(models.Post.id == post_id))
            post = result.scalars().first()
            if post:
                return post
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        ```
    * Update how we display `post.html` and `home.html` templates
        - `date_posted` display text were str and now it is datetime object --> need to convert it in the html files
        - `post.author` display text now need to update path to let user upload their own else use default
        - change the destination URL `url_for()` and display text `post.author.username` so when user click on an username --> it lead to that user's posts page
        - Code Demonstration:
        ```.html
                {% extends "layout.html" %}
        {% block content %}
        {% for post in posts %}
            <article class="content-section py-3 px-4 mb-4">
            <div class="d-flex align-items-start gap-4">
                <img class="rounded-circle article-img flex-shrink-0"
                    src="{{ post.author.image_path}}"
                    alt="{{ post.author.username }}'s profile picture"
                    width="64"
                    height="64"
                    loading="lazy">
                <div class="flex-grow-1">
                <div class="article-metadata mb-2">
                    <a class="me-2" href="{{url_for('user_posts_page', user_id=post.author.id)}}">{{post.author.username}}</a>
                    <small class="text-body-secondary">{{ post.date_posted.strftime('%B %d, %Y') }}</small>
                </div>
                <h2>
                    <a class="article-title" href="{{ url_for('post_page', post_id = post.id) }}">{{ post.title }}</a>
                </h2>
                <p class="article-content">{{ post.content }}</p>
                </div>
            </div>
            </article>
        {% endfor %}
        {% endblock content %}
        ```
- **Final Execution**:
    * Need to create user before create post due database dependencies 
    * when pydantic serialize the response at `{post.author}`, SQLAlcheny automatically load that user data 
    * Now with database, data are persisted through sever restart 
    * Finish GET and CREATE in CRUD operation HTTP methods --> dive into UPDATE & DELETE



## **Part 6: Adding PUT, PATCH, DELETE for CRUD operations of RESTs API**

- **To do:**
    * Finalise `CRUD` methods to have a full API where we can create, read, update and delete both users and post 
    * Configure `Cascade DELETE` method such that all the posts will be deleted along with the deleted users 
    * Test with the API docs and the HTLM frontend 

- **Build `UPDATE` method in REST API --> have 2 `UPDATE` methods:**
    * **PUT**: full replacement
        - Send all of the fields for that resource to replace
        - Like replace the record with a new version of that record 
    * **PATCH** : partial update
        - You only send what has or what need to be change
        - what you did not send will stay the same 
- **Update `PATCH` method in schema.py:**
    * **PATCH** request: make the all defined filed within the schema all optional
    ```schema.py
    #For PATCH method
    class PostUpdate(BaseModel):
        title: str | None = Field(default=None, min_length=1, max_length=100)
        content: str | None = Field(default= None, min_length=1)
    ```

- **Update the endpoints for `UPDATE` methods for both PUT and PATCH in main.py**
    * Since `PUT route` is the full replacement meaning client side will need to send entire new representation of the resources(post) not just the fields require changed. Therefore, we can use `PostCreate` from `schema.py` because it already require compulsory fields including *title*, *content* and *user_id* as well as sastisfy the `PUT` method definition
    ```python
    #PUT
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
        db.commit()
        db.refresh(post)
        return post
        
    #PATCH

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
    ```

- **Build `DELETE` method in our RestAPI**
    * `DELETE` endpoint usually response with the `204 SUCCESS` response(sucess response with no content) --> replace response model with status_code instead
    ```.py
    @app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
        result = db.execute(select(model.Post).where(model.Post.id == post_id))
        post = result.scalars().first()
        #check if the post exist to DELETE --> else 404 error
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post was not found")

        db.delete(post)
        db.commit()
    ```

- **HTTP Status Code Reference:**
    * *200 OK*: Successful GET, PUT or PATCH
    * *201 Created*: Successful POST for users and posts 
    * *204 No Content*: Successful DELETE
    * *400 Bad Request*: Duplicate username/email when create user 
    * *404 Not Found*: Resource does not exist(user or post)
    * *422 Unprocessable Entity*: Validation error(automatic from Pydantic)

- **Build `PATCH` method for `User` in our RestAPI**
    * Include `UserUpdate` schema in schemas.py:
    ```python
    class UserUpdate(BaseModel):
    username: str | None = Field(default= None, min_length=1, max_length=50)
    #pydantic EamilStr automatically validate the proper email format for us  
    email: EmailStr | None = Field(default=None, max_length=120)

    #Only lets user change which filename is referenced as their profile picture
    #No need full path because the image_path property within model.py has already build the full path
    image_file: str | None = Field(default=None, min_length=1, max_length=200)

    ```

    * Include endpoint for PATCH operation for user
    ```python
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
    ```

- **Build `DELETE` method for `User` in our RestAPI**
    * *Two options for deleting `User`(parent class of `Post`):*
        - If they have post --> prevent delete user(safe) 
        - Delete `User` and cascade delete all of their post --> pop up "are you sure.."
    * *Include `Cascade Delete` in model.py*
    ```
    posts : Mapped[list[Post]] = relationship(back_populates="author", cascade="all, delete-orphan")
    ```

    * *add `DELETE` endpoint for `User` in `main.py`*:
    ```python
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
    ```
- **Update user profile picture**
    * Right now, we need to manually put our picture in `media/profile_pics` and then patch at `api/users/{user_id}` --> we have ability to update the profile picture now but not uploading files
    * Later we will use the picture(file) upload functionalities 



## **Part 7: Synchronous vs Asynchronous in FastAPI - Optimize App by converting to `Async`**

- **What is the difference betwene `Synchronous` vs `Asynchronous`?**
    * `Synchronous(Subway)`: 
        - Only allow your program to run *one operation* at a time, in order, and each operation blocks until it finish before the next one start
        - If a `synchronous` function hit something slow(a database query, a network call,..), the entire program sits idle, unable to execute anything in meantime
    * `Asynchronous(McDonalds)`: 
        - Allow your program to handle mutiple tasks concurrently
        - It is usually misconcepted with *alway being faster*
        - When the route we defined hit `db.execute` it doesn't block the entire program. Instead, it tells the event loop: "I'm waiting on the database now — go ahead and run something else (another request, another coroutine) in the meantime, and come back to me when the database responds.
- **When to use `Synchronous` and when to use `Asynchronous`>**
    * `Synchronous`: 
        - Where plain def starts to strain — the thread pool has a limit
    * `Asynchronous`:
        - Concurrent load: lots of requests at the same time
- **Apply to current app**:
    * Using `Asynchronous` approache will help us avoid waiting external service such as database response, network request
    * IO Bound Tasks: situation like database querrying while waiting for database to response, external API call when waiting for network response

- **How FastAPI hanle `Synchronous` and `Asynchronous`?**:
    * When define normal `def function`:
        - FastAPI automatically hands off the function to the seperate worker thread pulled from thread pool
        - Meaning the event loop is free to keep handling other requests (including async ones) while your synchronous function blocks its own dedicated thread, not the shared event loop.
        - Prevent function from blocking the main event loop 

    * When define `async def function`:
        - API run the function directly in the main event loop(does not hands off to a worker thread like it does in `def`) but you must `await` for any IO operations
            * `await` is the mechanism that tells the event loop "I'm about to wait on something slow (network, disk, DB) — feel free to go run other tasks while you wait, and resume me when this is done.
        - If you do blocking IO without await --> prevent entire event loop --> worse than leaving it as default
        - Make sure to use it correctly
    * Choose which *approach* base on what your specific route does


- **Download dependecy `AIOS` for SQLite or `psychopg` for PostGres**:
    ```
    python -m pip install aiosqlite
    ```
    * Provide async `driver` for SQLite
    * SQLalchemy(abstraction layer) can then sue this driver for async operations
    * Struture:
    ```
    Your code (select(), Session, .execute())
        ↓
    SQLAlchemy (ORM/query-building layer — translates Python into SQL)
        ↓
    Driver (the thing that actually opens a connection and sends/receives raw data)
        ↓
    The database itself (SQLite file on disk)
    ```

- **Making changes to the current script**:
    * Convert `database.py` to async
    ```python
        #Synchronous
    # from sqlalchemy import create_engine
    # from sqlalchemy.orm import DeclarativeBase, sessionmaker

    #Asynchronous
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.orm import DeclarativeBase


    #tell which async driver to use for sqlite database instead of default blocking sqlite3
    SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"

    #build objet that manage the actual connectio to the database with update version that knows
    #how to hand back awaut operation
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread":False}
    )

    #Create an Async Session
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        #
        expire_on_commit=False
    )

    #share parent class for futre ORM models 
    #inheriting from Base is what lets SQLAlchemy discover and map current Class to an actual Table nbnbnbnb
    class Base(DeclarativeBase):
        pass

    #use generator
    async def get_db():
        async with AsyncSessionLocal() as session:
            yield session
    ```

    * Convert `main.py` to be asynchronous on the database
        - Change and import neccessary libraries for asynchronous changes
            - `asynccontextmanageer` is for *FastAPI lifespan handler* - modern way to run startup/shutdown code with asynchrnous connection
                * This is a function runs startup code(like database tables) before the app accept request
                * Then run cleanup code when it shuts down
            - `http_exception_handler` and `request_validation_exception_handler` used to automatically handle http exception instead writing manuaally building JSONResponse()
            - `AsyncSession` used to yield actual AsyncSession object which can help us to access the await-able methods for db
            - `selectinload` is eager loading tools to fetch the data at the same time upfront via extra batch one extra batched querry --> so it can avoid  a separate query for every individual related object accessed afterward
        ```python
        #delete JSON response
        rom contextlib import asynccontextmanager

        from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler

        # from sqlalchemy.orm import Session
        # Change normal Session to Async Session
        from sqlalchemy.ext.asyncio import AsyncSession

        #import select and load for eager loading relationships
        from sqlalchemy.orm import selectinload
        ```
    
        - Change from synchronous engine to asynchronous engine using lifespan
        ```python
        @asynccontextmanager
        async def lifespan(_app: FastAPI):
            #Startup code
            #engine.begin() run async connection which explicitly connect to AsyncConnection object
            async with engine.begin() as conn:
                #run_sync help us call and execute create_all method under async context
                await conn.run_sync(Base.metadata.create_all)
            #run application
            yield
            #Shutdown 
            await engine.dispose()
        ```

        - Convert our `route` to be async. Skip the code since it is too long, but few things to mention:
            * Switch from `def` to `async def`
            * Put `await` before database calling function
            * Put in `selectinload` where the querry access the relationship between models else no need. --> Need to be very precise on the relationship between models and the querry we are making

- **Important: the difference between synchronous and asynchronous SQLAlchemy**
    * In sync SQLAlchemy, `lazy loading` just work
        - For example: when we have a `Post` object, using template accessing `post.author` will just work without any issue since SQLAlchemy automatically run a querry to load that author as long as it is the relationship
    * IN async SQLAlchemy, `lazy loading` is not supported
        - Error if try to run since it require running asynchronous querry in an async context which not allowed
        - Solution: 
            * Run `eqger loading` with instead of `lazy loading` with `selectinload`
            * It tell SQLAlchemy to load the accessdata to be loaded immedietly with the main querry and store them in memory. This can avoid the `lazy loading` phenomenon. 

- **Convert our Exception Handler from Synchronous to Asynchronous using `fastapi.exception_handlers`(FastAPI default handler)**:
    ```python
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
    ```

- Best `Asynnchronous` use cases:
    - When you are making multipe independent, longrun IO operations
    - Calling external APIs
    - Have database running under high concurrency load 

- Best `Synchronous` use cases:
    -  When you have simple fast oprations
    - Calculation, image procssing
    - Cod clarity 
    - Sync only libraris
- Can use mix of 2 base on specific route needs
    * Since our route all use database --> all need async
- Common pratices for using `Asynchronous`
    - Dont use `Synchronous Database Session` in `async` function
    - Dont use request libraries in async since it is synchronous libraries

    



## **Part 8: Organize `Routes` into modules using `API router`(internal/code organization)**
- **Current Problem:**
    * Our `main.py` is packed too much endpoints for both frontend(HTML) and backend(API) which overload our eyes and other dev cognitive load if this is a production level project
    * Need to organize them in `modules` aka `routers` such that the `main.py` only have main functionalities to call those `routers`
- **Overview of our solutions**:
    * There are many way to organize the `module`, it can be by *version*, *domain*, *models*
    * In this tutorial, we gonna use *model* organization which is specific file for `User` and `Posts`
    * Common software development pratice in term of organizing our code:
        - You build up some functionalities
        - Then polish and organize them before adding more complexity  

- **Steps:**
    * create router directory
    ```
    routers/
        __init__.py      # empty, just marks this folder as a package
        users.py
        posts.py
    ```
    * Move user/posts routes into one file (routers/users.py shown, posts.py mirrors it)
    ```python
    # routers/users.py
    from typing import Annotated

    from fastapi import APIRouter, Depends, HTTPException, status
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession

    import model
    from database import get_db
    from schemas import UserCreate, UserResponse, UserUpdate

    #prefix means every route below only needs its remaining path (no "/api/users" repeated)
    #tags groups these routes together under "users" in the /docs UI
    router = APIRouter(prefix="/api/users", tags=["users"])

    #was @app.post("/api/users", ...) --> path becomes "" since prefix already covers it
    @router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
    async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
        ...  # body unchanged, just moved

    #was @app.get("/api/users/{user_id}", ...) --> path becomes "/{user_id}"
    @router.get("/{user_id}", response_model=UserResponse)
    async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
        ...

    @router.patch("/{user_id}", response_model=UserResponse)
    async def update_user(user_id: int, user_update: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
        ...

    @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
        ...
    ```
        - Why empty string in defined path for @router?
            - path in router is relative --> when include them in `main.py`, we are going to specify a prefix of /api/users
            - Empty string become the prefix we mentioned


    * update `main.py` to include those and keep the html route in the main.py to split front and backend
    ```python
    # main.py
    from routers import users, posts

    app = FastAPI(lifespan=lifespan)

    #wires each router's routes into the main app, using the prefix set on the router itself
    app.include_router(users.router)
    app.include_router(posts.router)

    #the create_user/get_user/etc. function bodies + their schema/model/db imports
    #are removed from main.py entirely, since they now live in routers/users.py
    ```
- **What is API router?**
    * It is FastAPI's tool for organizating route into modules
    * Define our route on router and call those routers in `main.py` instead of defining every route directly on `app`
    * `APIRouter` behaves just like `app` for route decorators (`@router.get`, `@router.post`, etc.) -- `app.include_router(...)` is what merges its routes into the real app at startup

- **Include `routers` in `main.py`**:
    * `.include_router()` connect the `router` with our app
    * `prefex="/api/posts(users)"` parameter adds that URL prefix to all routes in the `posts/users` file within routers package
    * `tag["users(posts)"]` parameter organize the for `/docs` page such that our posts/users endpoint are under a post/users header
    * **`Routes` function name for HTML(FE) and API(BE) can be conflicted if they have the same name because FastAPI use function name as the route name by default --> use unique descriptive function name for all the routes**
        ```
        ▸ users
            GET /api/users
            GET /api/users/{id}
            POST /api/users
        ▸ posts
            GET /api/posts
            POST /api/posts
        ```
    ```python
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    app.include_router(users.router, prefix="/api/posts", tags=["posts"])
    ```
## **Part 9:  Frontend Forms - Connecting JavaScript to Your API**

- **Current problem:**
    * The current frontend of the webpage is not interactive where user can not perform `CRUD` operation by themselves. It only available for developer through FastAPI docs interface
    * We will be adding and develop forms calling the API(our FastAPI server) such that it helps user perform `CRUD` Operations

- **Overview of our solutions:**
    * Use `Javascript` with fetch API to make those calls
    * Note: 
        - We will mainly focus on the on the API interaction by showing how the frontend sends the data to our endpoints
        - This is crutial steps if we want to change the whole frontend structure to React in the future
    * We will have a climpse on how `Javascript` will be the glue that connect the front and backend toghther for our app 
    * We already have the Backend setup that any client can access to
    * Since creating new user in `post` require `id` which need `Authentication`, we will be hard code some id for now just for `Javascript` logged-in user simulation --> `Authentication` will be added later on. --> This can help us test `Creating`, `Editing` and `Deleting posts`
    * For posts that not own by other user, we will implement functionalities that does not let those user perform `Edit` or `Delete` on those posts

- **Definitions:**
    * *Modal*: a pop-up window layered over the main page content
    * *Boostrap*:  is a free, open-source front-end framework used to build responsive, mobile-first websites. It provides pre-designed HTML, CSS, and JavaScript components—such as a 12-column grid system, navigation bars, buttons, and modals—allowing developers to create modern web interfaces quickly without writing code from scratch

- **Add modal to `layour.html`:**
    * This help us to have the modal modal in any page either `posts` or `individual` posts pages not just the `home` page
    * Using *boostrap* `New post` button to trigger a `New Post` modal:
    ```html
    <!-- NOTE: Once auth is set up, this button will only be visible when logged in -->
    <button class="btn btn-outline-light mb-2 mb-md-0 me-md-2"
            type="button"
            data-bs-toggle="modal"
            data-bs-target="#createPostModal">New Post</button>
    <!-- NOTE: Once auth is set up, this button will only be visible when logged in -->
    ```
    * Create standard *bootstrap modal* with the form intergrated inside of it 
        - `id = createPostModal`: reference this in our `Javascript` so it can catch and perform actions on those `ids`
        - our current form does not have method or attribute since we are intercepting the submission with `Javascript` --> more controllable over the API calling process
    ```html
        <!-- Create Post Modal -->
    <div class="modal fade"
            id="createPostModal"
            tabindex="-1"
            aria-labelledby="createPostModalLabel"
            aria-hidden="true">
        <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
            <h5 class="modal-title" id="createPostModalLabel">New Post</h5>
            <button type="button"
                    class="btn-close"
                    data-bs-dismiss="modal"
                    aria-label="Close"></button>
            </div>
            <form id="createPostForm">
            <div class="modal-body">
                <div class="mb-3">
                <label for="title" class="form-label">Title</label>
                <input type="text" class="form-control" id="title" name="title" required>
                </div>
                <div class="mb-3">
                <label for="content" class="form-label">Content</label>
                <textarea class="form-control" id="content" name="content" rows="5" required></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button"
                        class="btn btn-outline-secondary"
                        data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary">Post</button>
            </div>
            </form>
        </div>
        </div>
    </div>

    ```

- **Create a `response message` when a `post` is created or they encounter validation error**
    * Create `Success Modal` and `Error Modal` in `layout.html`:
    ```html
    <!-- Success Modal -->
    <div class="modal fade"
            id="successModal"
            tabindex="-1"
            aria-labelledby="successModalLabel"
            aria-hidden="true">
        <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header bg-success text-white">
            <h5 class="modal-title" id="successModalLabel">Success</h5>
            <button type="button"
                    class="btn-close btn-close-white"
                    data-bs-dismiss="modal"
                    aria-label="Close"></button>
            </div>
            <div class="modal-body">
            <p id="successMessage" class="fs-5"></p>
            </div>
            <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
        </div>
        </div>
    </div>

    <!-- Error Modal -->
    <div class="modal fade"
            id="errorModal"
            tabindex="-1"
            aria-labelledby="errorModalLabel"
            aria-hidden="true">
        <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header bg-danger text-white">
            <h5 class="modal-title" id="errorModalLabel">Error</h5>
            <button type="button"
                    class="btn-close btn-close-white"
                    data-bs-dismiss="modal"
                    aria-label="Close"></button>
            </div>
            <div class="modal-body">
            <p id="errorMessage" class="fs-5"></p>
            </div>
            <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
        </div>
        </div>
    </div>

    ```


- **Create a small `Javascript` utilities modules --> frontend setup without API interaction**:
    - `export function getErrorMessage(error)`:
        - FastAPI validation errors sometime is not a simple *string*, it can be an array(list) of `error objects`
        - This can be leaked on the UI if not handled decently
    - `export function showModal(modalId)`: 
        - This function is Boostrap's get or create instance method  with the modalID as parameter allow the button to fire modal when user click the button
    - `export function hideModal(modalID)`:
        - This function hide the modal and handle the case where the modal does not exists
    ```js
    // Error message extraction from API responses
    export function getErrorMessage(error) {
        if (typeof error.detail == "string"){
            return error.detail
        } else if (Array.isArray(error.detail)){
            return error.detail.map((err) => err.msg).join(". ");
        }
        return "An error occurred. Please try again.";
    }
    //show boostrap modal by ID'
    export function showModal(modalID){
        const modal = bootstrap.Modal.getOrCreateInstance(
            document.getElementById(modalID)
        );
        modal.show();
        return modal;
    }
    // Hide a Boostrap modal by ID
    export function hideModal(modalID){
        const modal = bootstrap.Modal.getInstance(
            document.getElementById(modalID)
        );
        if (modal) {
            modal.hide();
        }
    }
    ```
- **Write Javascript script inside `layout.html` to create an interative form(modal pop-up) when user want to create new post**:
    * Full valid flow from `frontend` to `backend` as long as user press button `New Post`:
        - *stage 1*: User clicks the `New Post` button in the navbar — its `data-bs-toggle="modal"` + `data-bs-target="#createPostModal"` attributes tell Bootstrap (no custom JS needed) to open the create-post modal
        - *stage 2*: User types into the `title` input and `content` textarea (both have `required`, so the browser blocks an empty submit) and presses the `Post` button (`type="submit"`), firing the form's `submit` event
        - *stage 3*: Our `submit` listener on `createPostForm` runs and calls `event.preventDefault()` — cancels the browser's default full-page form submission so JavaScript handles everything instead
        - *stage 4*: `new FormData(createForm)` collects every named input, and `Object.fromEntries(formData.entries())` converts it into a plain object `{title: "...", content: "..."}`
        - *stage 5*: `postData.user_id = 1` is bolted on manually — temporary hardcode until authentication exists, because the `PostCreate` schema requires a client-supplied `user_id`
        - *stage 6*: `fetch("/api/posts", {...})` sends a `POST` request with header `Content-Type: application/json` and body `JSON.stringify(postData)`; `await` pauses the handler until the server answers
        - *stage 7*: **(backend)** FastAPI matches the request to `create_post` in `routers/posts.py` (`@router.post("")` + the `/api/posts` prefix from `include_router`)
        - *stage 8*: **(backend)** Pydantic validates the JSON body against `PostCreate` (types + required fields), and the `Depends(get_db)` dependency opens an `AsyncSession` for this request
        - *stage 9*: **(backend)** The route queries `User` by `post.user_id` to verify the author exists (would raise `404 "User not found"` otherwise)
        - *stage 10*: **(backend)** A new `model.Post` ORM object is built, `db.add()`-ed, and `await db.commit()` writes the row into the `posts` table of `blog.db`
        - *stage 11*: **(backend)** `await db.refresh(new_post, attribute_names=["author"])` explicitly loads the `author` relationship — a freshly inserted row's relationship is not populated, and lazy-loading would raise in async context
        - *stage 12*: **(backend)** FastAPI serializes the ORM object through `response_model=PostResponse` (embedding the author as a nested `UserResponse`) and replies `201 Created` with a JSON body
        - *stage 13*: Back in the browser, `response.ok` is `true` (status 2xx), so the success branch runs; `await response.json()` parses the response body into the `data` object
        - *stage 14*: The success message is written into the success modal: `` `Post "${data.title}" created successfully!` `` → `#successMessage` via `.textContent`
        - *stage 15*: `hideModal("createPostModal")` closes the form modal, `showModal("successModal")` opens the success modal (both are our `utils.js` wrappers around Bootstrap's modal instance API)
        - *stage 16*: `createForm.reset()` clears the inputs so the form is empty the next time the modal opens
        - *stage 17*: A one-shot listener (`{ once: true }`) is attached to the success modal's `hidden.bs.modal` event — reload is *deferred* so the user actually gets to read the success message first
        - *stage 18*: When the user closes the success modal, `window.location.reload()` re-requests the page; the server re-renders the HTML with the new post now included in the list
    * Full error flow
        - *Status check fail* (`response.ok === false` — the server answered, but with an error status like `404 "User not found"` or `422` Pydantic validation error)
            - `await response.json()` parses the JSON error body, and `getErrorMessage(error)` normalizes the `detail` field (plain string *or* Pydantic's array of error objects) into one readable string written to `#errorMessage`
            - `hideModal("createPostModal")` closes the form modal, then `showModal("errorModal")` displays the error to the user
            - The page is **not** reloaded and the form is **not** reset — nothing was created, and the user's typed input stays intact for retry
        - *General Error Fail* (the `catch` block — `fetch` only *rejects* when the request never completed: server down, network lost; HTTP error statuses do **not** throw, which is why this is separate from the `response.ok` check)
            - A generic hardcoded message `"Network error. Please check your connection and try again"` is written to `#errorMessage` — there is no server response body to parse
            - `showModal("errorModal")` displays it (note: `hideModal("createPostModal")` is not called here, so the error modal appears stacked on top of the still-open form modal — worth fixing for consistency)
            - This branch also catches unexpected JS errors inside `try` (e.g. a non-JSON response body making `response.json()` throw), so the user always sees *some* feedback instead of a silent failure
    ```html
    <script type="module">
        //type="module" allow us to import other files in this case is utilies we defined
        import {getErrorMessage, hideModal, showModal,} from "/static/js/utils.js";
        // document represent the current loadpage, root of every interactive tags with javascript
        // getElementById search for any attributes match the value by id
        const createForm = document.getElementById("createPostForm");
        createForm.addEventListener("submit", async (event) => {
            // stop default form submission behaviour since reload the page which loss what we're typing in
            //  manually handle it with our javascript script fetching data and handle errors
            event.preventDefault();
        
            // Gather form data and convert it into a plain object {titleL "...", content: "..."}
            const formData = new FormData(createForm)
            const postData = Object.fromEntries(formData.entries());
            // Temporary - hardcode until authorization(post-login user)
            postData.user_id = 1;
            try{
                //POST to our API as JSON since we are prompt user to create a new `Post` in the `Posts` table
                // When user create new post, it convert the data to JSON and POST to our API
                const response = await fetch("/api/posts", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(postData)
                });
                // After Pydantic Validation, Database Verify the post does not exist before, status == ook then write success message
                if (response.ok) {
                    //convert from text response to json Object
                    const data = await response.json();
                    //Write the success message
                    document.getElementById("successMessage").textContent = `Post "${data.title}" created successfully!`;
                    //form close
                    hideModal("createPostModal");
                    //show the success modal after created successfully
                    showModal("successModal");

                    //clear form so it emptys next time
                    createForm.reset();

                    //Reload page after success modal is closed --> ensure the new post show up 
                    document
                        .getElementById("successModal")
                        .addEventListener(
                            "hidden.bs.modal", 
                            () => {
                                window.location.reload();
                            },
                            { once: true},
                        );
                } else {
                //create error message variable in json form
                const error = await response.json();
                //write error message
                document.getElementById("errorMessage").textContent = getErrorMessage(error);
                //hide the current modal
                hideModal("createPostModal");
                //show the error modal
                showModal("errorModal");
                }
            //show the general error modal like crashed API or network
            } catch (error) {
                document.getElementById("errorMessage").textContent = 
                "Network error. Please check your connection and try again";
                showModal("errorModal");
            }
        });

    </script>
    {% block scripts %}
    {% endblock scripts %}
    ```

- **Our current bug: the newest post is not at the top but rather bottm**:
    * Solution: update the `API(backend)` rather than `javascript` on the frontend where the newest post with the latest date will be put upfront
    * Sort `Posts` by date by updating the `GET api/posts` in `route/posts.py` and HTML element in `main.py`
        - `route/posts.py`:
        ```py
        result = await db.execute(
        select(model.Post)
        .options(selectinload(model.Post.author))
            #we are give the descendending order of the querry(router) instead of the data itself
        .order_by(model.Post.date_posted.desc())
        )
        ```
        - `route/users.py`
        ```py
        #Route/endpoints to response to the GET request for all the posts by a specific user
        @router.get("/{user_id}/posts", response_model=list[PostResponse])
        async def get_user_posts(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
            #check if the user exist
            result = await db.execute(
                select(model.User)
                .where(model.User.id == user_id)
                .order_by(model.Post.date_posted.desc())
        )
        ```
        - `main.py`
        ```py
        @app.get("/", include_in_schema=False, name="home")
        @app.get("/posts", include_in_schema=False, name='posts')
        # #the request parameter is the FastAPI mechanism for the route function access to the raw incoming http request object

        #Update the home route(return all posts) with the database included 
        async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
            result = await db.execute(
                select(model.Post)
                .options(selectinload(model.Post.author))
                .order_by(model.Post.date_posted.desc())
            )
            posts = result.scalars().all()
            return templates.TemplateResponse(
                request,
                "home.html",
                {"posts": posts, "title": "Home"}
            )

        @app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts_page")
        async def user_posts_page(request: Request, user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
            #does not need selectInload since it does not access relationship (post --> author)
            result = await db.execute(
                select(model.User)
                .where(model.User.id == user_id)
                .order_by(model.Post.date_posted.desc())
        )

        ```

- **Create `Edit` and `Delete` Function on Individual Post in HTML(frontend)** 
    * Edit post.html by adding and adjusting:
        - `edit/delte button`: ref to the delete and edit modal
        - `Edit Post modal`: A form of created content allow fixing
        - `Delete Post modal`: A confirmation modal asking if they really wanna delete it. 
    * Add Real Functionalities to those modals using `JavaScript`:
    ```html
        {% endblock content %}
    {% block scripts %}
        <script type="module">
        import {
        getErrorMessage,
        hideModal,
        showModal,
        } from "/static/js/utils.js";

        // Get post ID from Jinja2 template
        const postId = "{{ post.id }}";

        // Edit Post Form Handler
        const editForm = document.getElementById("editPostForm");
        editForm.addEventListener("submit", async (event) => {
        // Stop default form submission - we'll handle it with JavaScript
        event.preventDefault();

        // Gather form values into a plain object
        const formData = new FormData(editForm);
        const postData = Object.fromEntries(formData.entries());

        // Remove post_id from data cause we dont need that field to match the request with PostUpdate schema (it's in the URL, not the body)
        delete postData.post_id;

        try {
            // PATCH for partial update (just title and content, not post_id)
            const response = await fetch(`/api/posts/${postId}`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(postData),
            });

            if (response.ok) {
            document.getElementById("successMessage").textContent =
                "Post updated successfully!";

            hideModal("editModal");
            showModal("successModal");

            document
                .getElementById("successModal")
                .addEventListener(
                "hidden.bs.modal",
                () => {
                    window.location.reload();
                },
                { once: true },
                );
            } else {
            const error = await response.json();
            document.getElementById("errorMessage").textContent =
                getErrorMessage(error);

            hideModal("editModal");
            showModal("errorModal");
            }
        } catch (error) {
            document.getElementById("errorMessage").textContent =
            "Network error. Please check your connection and try again.";
            showModal("errorModal");
        }
        });

        // Delete Post Handler - listen for click on delete button
        const deleteButton = document.getElementById("confirmDelete");
        deleteButton.addEventListener("click", async () => {
        try {
            // DELETE request - no body needed, post_id is in the URL
            const response = await fetch(`/api/posts/${postId}`, {
            method: "DELETE",
            });

            // 204 = No Content (success)
            if (response.status === 204) {
            // Post is gone, redirect to home page
            window.location.href = "/";
            } else {
            const error = await response.json();
            document.getElementById("errorMessage").textContent =
                getErrorMessage(error);

            hideModal("deleteModal");
            showModal("errorModal");
            }
        } catch (error) {
            document.getElementById("errorMessage").textContent =
            "Network error. Please check your connection and try again.";
            showModal("errorModal");
        }
        });
        </script>
    {% endblock scripts %}
    ```


## **Part 10: Create Authentication --> who are you?**


- **What is `Authentication` and current `Problem`?**
    * We are using hard-coded user_id --> anybody can access the app and perform CRUD on it
    * `Authentication` is used in web development to verify the identity of a user or system before granting access to protected resources
    * To our appllication, anyone could call our API and perform CRUD on anything
- **What should be the solution?**
    * We'll build the backend *authentication infrastucture* including:
        - `Password Hashing`: is how a server can verify your password without ever storing it. It's the cornerstone of the auth work you're about to do
            - Never store customer password within the database 
            - hash function takes any input and produces a fixed-size scrambled output 
            ```py
            hash("hunter2")  →  "$2b$12$KIXn8...Zq9uHm"
            ```
            - Why the field can be null?
                - NULL gets a meaning of its own
                - Once auth exists, hashed_password = NULL isn't just "missing data" — it's a state: "this account has no local password and cannot log in with one." No password, no create account
                - Or can be used for OAuth with no password needed
        - `JSON web token` utilities:
            * User will login and register with `JSON web token`(JSON Web Token `(JWT)` is a small, safe string used to share data between two groups. People use it for user login on websites and apps)
            * By automatically gain user ID from `JWT`, the api can verify ownership with `schema` before user can peform CRUD on the posts within the app
            * `JWT components`: It has 3 components including:
                - Header: contain algorithm and type
                - Payload: Contain Data and Expiration
                - Signature: Prove that the token's data has not been faked with. It is created by our serete key --> only our server can create valid token for user request
                All three parts are base64 encoded, sperated by the dot

    * Then, it is when we build registration and login form on the frontend and wire them altoghether
        
- **Install packages**:
    * `"pwdlib[argon2]"`: Modern choice for password hashing
    * `pyjwt`: JSON web token operations for FastAPI
    * `pydantic-settings`: managing configuration
        - Why not `python-dotenv?`:  
            * choosing robust, type-safe configuration management over basic string loading
            *  While python-dotenv simply reads .env files and injects them as strings into os.environ, pydantic-settings validates, casts, and structures your entire application config
            * centralize all of the configuration into on setting module
            * Validate type automatically
            * It fails dast with clear errors
            * It use secrete key from Pydantic so that it wont be exposing secrete information within logs or print satement

- **2 Approaches For The Database Change Intergrating Authentication**
    * **Delete current database**:
        - Why?
            - We are adding a required fields(at least one new column — the hashed password) to our users model --> SQLite does not make it easy to add non-nullable columns to existing table because `creat_all` skip existing tables --> Therefore it does not compares the existing tables against the model --> does not see a new change
        - How?
            - Delete `blog.db` and start fresh with `modle.py`
            - Add `password_hash` field to `User` modle: 
            ```py
            #password hashing
            password_hash: Mapped[str | None] = mapped_column(String(200), nullable=False)
            ```
    * **Database migrations**
        - Why?
            - Production apps can't torch their data on every schema change, so they use a migration tool

- **Update the schema**
    * Update `UserCreate`: Include the password validation field everytime user create password
    ```py
    class UserCreate(UserBase):
    password: str = Field(min_length=8)
    ```
    * Improve Data Privacy Concern(email) by differentiate `UserResponse` into `UserPubic` and `UserPrivate`:
    ```py
        #Reposne Model --> divide into seperate private and public reposnse
    class UserPublic(BaseModel):
        model_config = ConfigDict(from_attributes=True)
        id : int
        image_file: str | None
        image_path: str

    class UserPrivate(UserPublic):
        email: EmailStr
    ```

    * Add `Token Schema`: Validate login reponse with JWT
    ```py
    #Token schema for login responses
    class Token(BaseModel):
        access_token: str
        token_type: str
    ```

- **Create a new configuration file `config.py`:**
    * Know the difference:
        - `.env` — a plain text file holding the values, especially secrets. Never committed to git aka enviroment variable
  
        - `config.py` — Python code defining which settings exist, their types, and how to load them. Committed to git.
        - What pydantic-settings replaces is `python-dotenv` the *loading mechanism*, not the `.env` file itself.
        - Configuration process have similar syntax as setting pydantic schema
    * Code Explanation:
        - `model_congig = SettingConfigDict(env...)`: This tell the pydantic_setting where to find the source for validation - In this case is the `.env` file
        - `secret_key: SecretStr`: instead of visible `str` key that can be read by anyone accessing the `log`(log are server narrating events as they happen, ususally wrriten into diles `app.log` and shipped to log services --> help debug a server without watching it live), it will wrap entire value in `aterisk` form which prevent the secrets to printed out as `str()` and `repr()`  in *print(settings) statment or exceptions*. Actual values can only be access with explicit call `.get_secret_value()`
        - `algorithm: str="HS256"`: Is the standard code for JWT
        - `access_token_expire_minutes: int= 30`: how long a token stays valid after login

        ```py
        from pydantic import SecretStr
        from pydantic_settings import BaseSettings, SettingsConfigDict

        class Settings(BaseSettings):
            #This line tell pydantic where to find the sources proatively --> then validate those sources --> in this case is .env files
            model_config = SettingsConfigDict(
                env_file = ".env",
                env_file_encoding="utf-8"
            )
            #Setting field
            secret_key: SecretStr
            algorithm: str= "HS256"
            access_token_expire_minutes: int= 30

        settings = Settings() #loaded from .env file

        ```
    * **How dooes pydantic-settings know which enviroment variable maps to whichof the defined field?**
        - Field name match enviroment variable name(Not case-sensitive) --> easily match enviroment variable in `.env`
        - Pydantic help all of the data type conversion problem when validate
        - It also have the priority order: if the variable is setup in the system enviroment variables, it gonna win out the `.env` file
    
- **Create `.env` file**:
    * Create `secret key`:
        - How does it works with `JWT`?: HTTP is stateless — no identity persists between requests. Instead of a server-side session, the server issues a JWT at login: a token holding identity claims, stored by the client and attached to every request. The payload is plain (base64) JSON — anyone can read it or craft their own — so claims alone prove nothing. The secret key, held only by the server, solves this: the server signs(hash the token) each token's payload with the key and algorithm (HMAC-SHA256), and on every request re-computes that signature to check the token was issued by the server and not modified since with the key. The client carries the token, never the key — forging a valid token would require the key itself.
    * Create `secret_key`:
        ```powershell
        #Generate the secret key command
        python -c "import secretes; print(secrets.token_hex(32))"
        ```
- **Create `auth.py` file for authentication utilities including password hashing and token creation**
    * Definition and Configuration Setup
        - `password_hash = PasswordHash.recommended()`: create password hasher using Argon2 with recommended default setting
        - `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")`: extract the authetnication token's header when the client send it

    * Hash and Verify password functions
        - `hash_password` function used for Registration process and the hashed password will be stored in the datbase
        - `verify_password` used at every login. It can't just re-hash and compare strings (the salt makes every hash different) — verify reads the salt out of the stored hash, hashes the attempt with that same salt, then compares. That's why it needs both arguments.
            - Every login
            ```
            1. read stored hash from DB
            2. extract the SALT part out of it
            3. hash(typed_attempt + that same salt)
            4. compare result to the HASH part → True/False
            ```
        ```py
        #hash_password function
        def hash_password(password: str) -> str:
            return password_hash.hash(password)

        #verify if the plain password match the hashed password
        def verify_password(plain_password: str, hashed_password: str) -> bool:
            return password_hash.verify(plain_password, hashed_password)
        ```

    * **Create Access Token function**
        - The login stamp: called once, right after `verify_password` returns `True`. Takes the claims (`{"sub": user.id}`), stamps a deadline, signs with the secret, returns the token string
        - Flow: `data` --> copy --> add `exp` (now + 30 min, or custom) --> `jwt.encode(payload, SECRET, HS256)` --> `"header.payload.signature"`
        - Line by line:
            - `def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str`: `data` = claims to embed; `expires_delta` = optional custom lifetime (omit --> settings default); returns the token string
            - `to_encode = data.copy()`: dicts are passed by reference, so the next lines would mutate the caller's dict --> copy first, modify the copy only
            - `if expires_delta: expire = datetime.now(UTC) + expires_delta`: caller gave a custom lifetime --> deadline = now + that. `UTC` so the timestamp means the same on every server
            - `else: expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)`: no override --> use the config default (30 min from `.env`/`config.py`)
            - `to_encode.update({"exp": expire})`: write the deadline into the payload under `exp` --> the JWT spec's reserved claim name. `jwt.decode` looks for exactly this key later and refuses expired tokens; this line only records it
            - `jwt.encode(to_encode, settings.secret_key.get_secret_value(), algorithm=settings.algorithm)`: build the token = base64(header) + base64(payload) + HMAC-SHA256 signature over both, keyed with the secret. `.get_secret_value()` unwraps the `SecretStr` box --> the real key string (only used here and in `verify_access_token`)
            - `return encoded_jwt`: hand the string back --> the login route wraps it in the `Token` schema --> `{"access_token": ..., "token_type": "bearer"}`
        - `sub` / `exp` are JWT spec claim names (`sub` = subject/who, `exp` = expiry/until when) --> spelling matters because `jwt.decode` checks them by name
        - Analogy: a hotel keycard --> encoded with your room (`sub`) and checkout time (`exp`), stamped by the front desk's machine (secret). Doors read it, only the desk can make it
        - Code:
        ```py
        #create access token
        def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.now(UTC) + expires_delta
            else: 
                expire = datetime.now(UTC) + timedelta(
                    minutes=settings.access_token_expire_minutes
                )
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(
                to_encode, 
                settings.secret_key.get_secret_value(),
                algorithm=settings.algorithm
            )

            return encoded_jwt
        ```

    * **Verify Access Token function**
        - The mirror image of `create_access_token` --> the door's card reader. Takes the raw token string (as extracted by `oauth2_scheme`), returns the `sub` (user id) if valid, `None` if not --> soft failure so the caller decides the response (usually 401)
        - Flow: `token` --> `jwt.decode(secret, [HS256], require exp+sub)` --> payload dict --> `payload["sub"]`; any failure (bad signature / expired / malformed / missing claim) --> `None`
        - Line by line:
            - `def verify_access_token(token: str) -> str | None`: input = token string; output = user id as string, or `None`
            - `try:`: PyJWT reports every failure by **raising**, not returning `False` --> the whole decode is wrapped
            - `jwt.decode(token, ...)`: the `xxxxx.yyyyy.zzzzz` string to check
            - `settings.secret_key.get_secret_value()`: the same key used to sign --> HS256 is symmetric, so decode recomputes the signature and compares it to the token's third part. Mismatch = tampered or forged
            - `algorithms=[settings.algorithm]`: explicit **allowlist** of accepted algorithms (a list, and required). Blocks the classic attack where a forged token's header says `"alg": "none"` (no signature) or swaps algorithm --> decode only accepts what is listed
            - `options={"require": ["exp", "sub"]}`: checklist of claims that **must exist** in the payload. Needed because `exp` is only enforced *if present* --> a token with no `exp` would otherwise pass forever; `sub` is required because the return line depends on it. Missing either --> `MissingRequiredClaimError`
            - `except jwt.InvalidTokenError: return None`: the base class of every PyJWT failure (`ExpiredSignatureError`, `InvalidSignatureError`, `DecodeError`, `MissingRequiredClaimError`) --> one `except` catches them all. Deliberately no detail --> caller says "invalid credentials" without telling an attacker *which* check failed
            - `else: return payload.get("sub")`: `else` on a `try` runs only when no exception occurred --> `payload` is now a trusted dict (signature valid, not expired, claims present) --> hand back the user id
        - Analogy: passport check --> the officer verifies the stamp is genuine (signature) but also requires the expiry field and name field to physically exist (`require`). A genuine passport with a blank expiry is still refused
        - Code:
        ```py
        #verify access token
        def verify_access_token(token: str) -> str | None:
            #Verify a JWT access token and reuturn the subject's id if valid
            #--> store user_id in sub field before
            try:
                payload = jwt.decode(
                    token,
                    settings.secret_key.get_secret_value(),
                    algorithms=[settings.algorithm],
                    options={"require": ["exp", "sub"]}
                )
            except jwt.InvalidTokenError:
                return None
            else:
                return payload.get("sub")
        ```


    * **Update router `users.py` so that we can work with credentials** 
        - What is `OAuth2`: A standard describing how client obtain and use tokens. Designed primarily for gratting access to set of resources such as remote APIs or User Data
        - What is `OAuth2PasswordRequestForm`? built-in FastAPI dependency class that extracts user login credentials from form data(username and password) then pass to the login route 
        - update `import` section:
            * `func` SQL Alchemy library used for SQL functions ORM
        ```py
        from sqlalchemy import func, select
        from fastapi.security import OAuth2PasswordRequestForm
        from auth import (
            create_access_token, 
            hash_password, 
            verify_access_token, 
            verify_password
        )
        from schemas import UserCreate, UserPublic, UserPrivate, Token, UserUpdate, PostResponse

        from config import settings
        ```
        - Fix the routers
            * `create_user`:
                * Update response model:
                ```py
                response_model = User private`
                ```
                * Update the the `username` checking to be case-insensitive to prevent duplicated user
                ```py
                result = await db.execute(
                select(model.User)
                .where(func.lower(model.User.username) == user.username.lower()
                    )
                )
                ```
                *Update the field for `new_user` created:
                ```py
                new_user = model.User(
                username=user.username,
                #make sure the email always lowercased
                email=user.email.lower(),
                password_hash = hash_password(user.password)
                )
                ```
        - Add `Post: "/token"` route:
            * /token = form → email lookup → verify_password → create_access_token → Token; the only place the password is ever checked.
            ```py
            @router.post("/token", response_model=Token)
            async def login_for_access_token(
                form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: Annotated[AsyncSession, Depends(get_db)]):
                #look up user by email instead of username(default by OAuth2)
                # Note: OAuth2PasswordRequestForm uses "username" field, but we treat it as email
                
                #check if the username(email) exist within the database using SQLAlchemy
                result = await db.execute(
                    select(model.User)
                    .where(func.lower(model.User.email) == form_data.username.lower()
                    )
                )
                user = result.scalars().first()

                #verify if user exist or password entered is correct
                #Do not reveal which one failed for security reason
                if not user or not verify_password(form_data.password, user.password_hash):
                    raise HTTPException(
                        status_code= status.HTTP_401_UNAUTHORIZED,
                        detail="Incorrect email or password",
                        headers={"WWW-Authenticate": "Bearer"}
                    )

                #create access token with user_id subjet
                access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
                access_token = create_access_token(
                    data = {"sub": str(user.id)},
                    expires_delta= access_token_expires
                )
                #Construct an instance of Token Pydantic Schema and return as JSON to client and docs server
                return Token(access_token=access_token, token_type="bearer")
            ```
        - Add `"GET: /me"` route for the `frontend`:
            * Put this route before router `GET {user_id}` because fastAPI mathces routes in order
            * /me = extract → verify → parse sub → load row → UserPrivate; the frontend calls it once per page load to learn who's logged in. 
            * Have `int()` guard for 401 error instead of 500 `internal error`
            * How the frontend use it: On `loading page` right after `login`, fetch("/api/users/me") with the token → save the JSON in currentUser → render name/avatar, show Edit/Delete on their own posts. 401 → treat as logged out.
        ```py
        @router.get("/me", response_model=UserPrivate)
        async def get_current_user(
            #pull the token out of the Authorization header
            token: Annotated[str, Depends(oauth2_scheme)],
            db: Annotated[AsyncSession, Depends(get_db)]
        ):
            #get the current authenticated user
            user_id = verify_access_token(token)
            if user_id is None:
                raise HTTPException(
                    status_code = status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    #bearer is the auth scheme where presenting the token is the whole proof
                    #who own this token will be authroized to proceed
                    headers={"WWW-Authenticate:": "Bearer"}
                )

            #validate the user_id is an integer(defense against malformed JWT)
            #This does not belong to Pydantic but rather the JWT payload
            try:
                user_id_int = int(user_id)
            except(TypeError, ValueError):
                raise HTTPException(
                    status_code= status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate:": "Bearer"}
                )

            #look up the user within the database
            result = await db.execute(
                select(model.User)
                .where(model.User.id == user_id_int)
            )

            user = result.scalars().first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            return user
        ```
    * **Add more html `login.html`, `register.html` page**
        - `login.html`:
            * When we submit the form, we send the `formData` format because we OAuth2PasswordRequestForm expect formData type instead of JSON
            * If the `response success`: We store the token in localStorage
                * The bearer-header approach (client stores token, sends `Authorization: Bearer`) works for every client type — web, mobile, CLI — which is why APIs standardize on it. In the browser the token is kept in `localStorage`.
                * Weakness: any JS on the page can read `localStorage`, so a cross-site scripting (XSS) injection
                can steal the token. Defense = prevent injection (escape all user content: Jinja `{{ }}`,
                `textContent` not `innerHTML`) + short token lifetime to limit the damage window.
                * `HttpOnly` cookies are the safer web-only choice (JS can't read them) but need CSRF protection
                (`SameSite`) and are awkward for non-browser clients.


        - `register.html`:
            * `frontend` validation + live password-match check → 
            * JSON POST {username, email, password} to /api/users → success modal on `frontend`
            * if the response is success, then show success modal and redirect to /login else show error modal if it is not valid 
            * Server hashes the password, browser never sends confirmPassword.
    * **Add `auth.js` for frontend validation**
        - **#1:** check if the cached `currentUser` and `fetchPromise` has been called to prevent dupplicate API call since multipple part of the page might call the current user(from API) at the same time --> we dont want to spam that 
            - `currentUser`: caches the `/me` response in a browser variable (page-lifetime memory, NOT the database) --> later calls return it instantly, no duplicate request
            - `fetchPromise`: caches the receipt (promise) of the in-flight `/me` request --> callers arriving while the answer hasn't landed yet await the SAME receipt instead of firing their own fetch; when the response arrives it resolves for all of them, then the receipt is cleared (`finally`) and `currentUser` takes over
        - **#2:** Read the token from `localStorage` (it was stored there by `setToken()` in `login.html` after `/token` responded)
            - `localStorage` is a small key-value store built into the browser, per website, that survives page reloads and browser restarts. 
            - This solves the problem where a `JS` variable dies when the page unloads --> without persistent storage, navigating between pages would wipe the token and log the user out instantly
        - **#3**: if no `currentUser`: fetch the user from the API, why?
            - Fetch the backend route because the frontend doesn't know who the user is — it only holds an opaque token string. 
            - The backend is the only party that can turn that string into a user (it holds the secret key and the database) --> returns the user as a JSON response, and the FRONTEND renders from it.
            - Calling the backend also means the token gets verified for free --> signature + expiry checked by `verify_access_token` on the server.
        - **#4**: three outcomes:
            - response ok --> cache in `currentUser` + return the user
            - 401/not-ok --> the token is dead --> remove it from `localStorage`, return null (page renders as logged-out; no redirect, `logout()` is not called)
            - network error (`catch`) --> return null but KEEP the token --> the token isn't proven bad, the network is
        - **#5**: Helper functions
        ```js
        //auth.js is frontend only, and it's not tied to login.html specifically; 
        // it's a shared browser module that every page imports. 
        //Cache" = keep a copy of an answer you already fetched, so you don't fetch it again.
        let currentUser = null;
        let fetchPromise = null;

        export async function getCurrentUser() {
        // user cache: is the currentUser variable store the copy of `/me` answer so no more request need to be called
        // if we have the cached user --> return that user immediately
        if (currentUser) {
            return currentUser;
        }

        // Return in-progress fetch to prevent duplicate API calls
        if (fetchPromise) {
            return fetchPromise;
        }
        //store the token in localStorage to prevent token being wiped off  due inpersistent storage
        const token = localStorage.getItem("access_token");
        if (!token) {
            return null;
        }

        fetchPromise = (async () => {
            //Fetch the backend route Because the frontend doesn't know who the user is — it only holds an opaque token string request by client side. 
            // The backend is the only party that can turn that string into a user then return the strintified JSON response and render it .
            // Also since it call backend, it can automatically validte the token since we define in auth.py
            try {
            const response = await fetch("/api/users/me", {
                headers: {
                Authorization: `Bearer ${token}`,
                },
            });

            if (response.ok) {
                currentUser = await response.json();
                return currentUser;
            }
            // if the token expire or invalid, we gonna remove the token from the localStorage
            localStorage.removeItem("access_token");
            return null;
            } catch (error) {
            console.error("Error fetching current user:", error);
            return null;
            } finally {
            fetchPromise = null;
            }
        })();

        return fetchPromise;
        }
        ```

    * **Update the `layout.html` nav bar right side into the `auth aware` version**
    ```html
    <div class="navbar-nav">
        <div id="loggedInNav" class="d-none">
            <button class="btn btn-outline-light mb-2 mb-md-0 me-md-2" type="button" data-bs-toggle="modal"
                                data-bs-target="#createPostModal">New Post</button>
            <span id="usernameDisplay" class="navbar-text me-md-2"></span>
            <button class="btn btn-outline-light mb-2 mb-md-0 me-md-3" type="button"
                                id="logoutBtn">Logout</button>
            </div>
            <!-- Shown when logged out -->
            <div id="loggedOutNav">
                <a class="btn btn-outline-light mb-2 mb-md-0 me-md-2" href="{{ url_for('login_page') }}">Login</a>
                <a class="btn btn-light mb-2 mb-md-0 me-md-3" href="{{ url_for('register_page') }}">Register</a>
    ```
    * **Update the auth state management into `layout.html`**
        - function `updateAuthUI` check if we have the current cached user. If it does then it:
            * Show the loggedin nav using bootstrap utility --> cleaner than inline style
            * Display the `user email`
            * Hide the loggedout nav
        ```html
                <!-- Auth State Management -->
        <script type="module">
        import { getCurrentUser, logout } from '/static/js/auth.js';

        // Update navbar based on auth state
        async function updateAuthUI() {
            const user = await getCurrentUser();
            const loggedInNav = document.getElementById('loggedInNav');
            const loggedOutNav = document.getElementById('loggedOutNav');

            if (user) {
            loggedInNav.classList.remove('d-none');
            loggedInNav.classList.add('d-flex');
            loggedOutNav.classList.add('d-none');
            document.getElementById('usernameDisplay').textContent = user.email;
            } else {
            loggedInNav.classList.add('d-none');
            loggedInNav.classList.remove('d-flex');
            loggedOutNav.classList.remove('d-none');
            }
        }

        // Logout handler
        document.getElementById('logoutBtn').addEventListener('click', logout);

        // Update UI on page load
        updateAuthUI();
        </script>
        ```
        - `logout button`  to run the `logout function`
        - call `updateAuthUI()` at the end on page load: It runs automatically on every page load and switch the navbar to match the current auth state, if `/me` confirmed --> logged in, otherwise, logged out
    * **Update the `main.py` with login and register route for the frontend** 
        ```py
        @app.get("/login", include_in_schema=False)
        async def login_page(request: Request):
            return templates.TemplateResponse(
                request,
                "login.html",
                {"title": "Login"}
            )

        @app.get("/register", include_in_schema=False)
        async def register_page(request: Request):
            return templates.TemplateResponse(
                request,
                "register.html",
                {"title": "Register"},
            )
        ```
    * * **Test on both the frontend and Swagger UI: login issues a token (password check) and protected routes accept it (/me returns the user)**
    
## **Part 11: Use Authorization to protect our routes and make sure users are authorized --> what you are allowed to do?**

- **What is `Authorization` and current `Problem` we ae facing?**
    * We have implemented `authentication` but havent actually used it 
    * Our UI testing is showing that the appliation still let any user modify the current user posts(since user_id is hardcoded everywhere) becasue we are not checking who is doing the request 
    * `Authentication` is used in web development to grant certain access to auhenticated user only.
    * Still, anyone could call our API and perform CRUD on anything
- **Solutions**
    * We want to limit post creation, patch, delete actions only to the current logged in user
    * Create reusable `getCurrentUser dependecies` for the backend routes
    * Delete the `user_id` field from schemas that contain it 
    * Fix the hardcoded value on the frontend with real authentication
    * Add ownership check
    * Build an `account page` for *profile management*

- our current `PostCreate(PostBase)` in `schema.py` have the fixed `user_id` in the request body:
    * This means that anyone can claim to be any user just by sending different id
    * We only want the authenticated user to create or post by themselves
    * Solutions:
        - Get `user_id` from the `token`(token are issued by our server so we can trust it) so we know who create the token request and when
    * Implementation:
        - Create `getCurrentUser() dependencies` in `auth.py` for other internal authenticatio requires from backend endpoints
        - Add neccessary library for building `dependencies` function
        ```py
        from typing import Annotated
        from fastapi import Depends, HTTPException, status
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import AsyncSesion
        import model
        from database import get_db
        ``` 