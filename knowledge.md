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
        - Benefit use `url_for`:
            * If you ever change your routes or change the mount path --> all the link will be updated



## **Part 3: Path Parameters - Validation and Error Handling** 

- Path URL paramter:
    * Use to grab a single post with individual API end point and have view of a specific page
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