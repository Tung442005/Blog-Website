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
        - With CRUD in Fast API, it only knows about the routes we define action with not a full folder with plain files
        - By Mounting those static files, we tell the server to serve everything under this folder directly(URL path)
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
        - Benefit use `urlcccccbxzcczxcbccxcczccczccccxczccxcbcbccccccccbcxzcccbccxbcnccczxbccccccbcc_for`:
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
        - Build response mdoel to our endpoints, which tell FastAPI exactily we are going to return 
        - This allow FastAPI doc to return the exact field, type and validation rules


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

- Problem statements:
    * As we use the posts lists --> it only store the data within the local machine's memory. Therefore, when the server is restarted, the posts list is recreated with the harded-code only 
    * Any posts that we create are going to dissapear
    * Therefore, we need database to persist the data across restarts --> use database
- Programming technique that connects object-oriented code to relational databases. It lets developers perform database actions using native programming language objects instead of writing raw SQL queries
- What to use in this projects?
    * Use SQL Alchemy library to interact with the database
    * At first, just use SQL lite to build a database --> then move to Postgre SQL with configuration change(connect different URL) with the code staying the same
    * Set up relationship between schemas --> easier to validate

- Application Architecture:
    * Database Models: 
        - Store the data
        - Contain ORM sepcific features like relationship
    * Pydantics Schema: Data Validation
        - Define API contract
    * API route: API endpoints handle the actual request

-  Why using seperate models instead of just one combination?
    * Better controls
    * Better for learning purpose
    * Industry stanard

- Full process(Overall Picture):
    * RequestS sent to the endpontS
    * Pydantic Validate it 
    * SQL stores or retrieves the data
    * Pydantic formats the response --> The response goes out 

- Create Database:
    * `DATABASE_URL` tell the SQL Alchemy where to connect for SQL lite, blog.db is created automattically
    * `Engine` variable is the object control & manage connection pool to the database 
        - `"check_same_thread":Fasle` is SQLite specific since SQL light normally only allows one thread but FastAPI handles multiple request across thread --> need to disable it
    * `SessionLocal` is the factory that creates database sessions --> the sessions si basically a transaction with the database  --> Each request gets its own sessison
        - This is waht you actually use to query/insert/update
        - Set `autocommit= False` and `autoflush=False` because we want to control when changes are commited --> standard FastAPI implementation
    * `DeclarativeBase`:
    * `get_db()` is a dependency function that provide sessions to our route(geneator using yield)
        - `With` statement make the session work as a context manager --> ensure clean up if error occur
    * Dependency injection: 


- Create Database Models: Define our database tables using SQL Alchemy OM
    * UTC is the new Python datetime library
    * the `Mapped[...]` annotation says what Python type, `mapped_column(...)` says how it behaves as a column: primary key, nullable, unique, foreign key, default value, explicit SQL type override, etc.
    * 