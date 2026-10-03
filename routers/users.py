from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


import model
from auth import (
    CurrentUser,
    hash_password,
    create_access_token, 
    verify_password
)
from database import get_db
from schemas import UserCreate, UserPublic, UserPrivate, Token, UserUpdate, PostResponse, PaginatedPostsResponse

from config import settings

from PIL import UnidentifiedImageError
from starlette.concurrency import run_in_threadpool
from image_utils import delete_profile_image, process_profile_image


#Define router instead of app 
router = APIRouter()


#Route to response to CREATE requet creating new user
@router.post(
    "",
    response_model=UserPrivate,
    status_code=status.HTTP_201_CREATED
)
async def create_user(user: UserCreate, db :Annotated[AsyncSession, Depends(get_db) ]):
    #check if a username already exist when we create a new user

    #Build and runs a SQL query to check where username exist
    result = await db.execute(
        select(model.User)
        .where(func.lower(model.User.username) == user.username.lower()
            )
        )

    #check matching user was found within the server using the result query above and get the first user_object if it exist
    #scalars() is used to turn each rows in tuple-like containers returned from db.execute to Scalar result(single enity) which help us get plain User objects directly
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )


    #Build and runs a SQL query to check where user email  exist
    result = await db.execute(
        select(model.User)
        .where(func.lower(model.User.email) == user.email.lower())
        )

    #check matching user was found within the server using the result query above and get the first user_object if it exist
    #scalars() is used to turn each rows in tuple-like containers returned from db.execute to Scalar result(single enity) which help us get plain User objects directly
    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    #If non of the above exist --> None --> Store that user with these field
    new_user = model.User(
        username=user.username,
        #make sure the email always lowercased
        email=user.email.lower(),
        password_hash = hash_password(user.password)
    )
    #IO: communicate with something outside istself, we are talking about database in this case
    #stages the insertt --> adding the objects to the session pending list(no IO) which does not require await
    db.add(new_user)

    #Execute and save to the database
    await db.commit()

    #reload the object from the database 
    await db.refresh(new_user)

    #return new_user and Pydantic will automatically convert that to a user response like what we setup with response model
    return new_user

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

"""
# User call this endpoints directly from the webUI
# Protected route: called by the frontend on page load / right after login.
# It sends the current request with their token and asks "who am I?" -->  validate the current user token and return the user data
# If authenticated --> Returns the token's owner as UserPrivate (email included --> it's their own account).
# Frontend need to know who is currently in the login by getting this router
# Then the Frontend stores the user response to render name/avatar and show Edit/Delete on that user's posts.
"""
@router.get("/me", response_model=UserPrivate)
async def get_current_user(current_user: CurrentUser):
    # #get the current authenticated user
    # user_id = verify_access_token(token)
    # if user_id is None:
    #     raise HTTPException(
    #         status_code = status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid or expired token",
    #         #bearer is the auth scheme where presenting the token is the whole proof
    #         #who own this token will be authroized to proceed
    #         headers={"WWW-Authenticate:": "Bearer"}
    #     )

    # #validate the user_id is an integer(defense against malformed JWT)
    # #This does not belong to Pydantic but rather the JWT payload
    # try:
    #     user_id_int = int(user_id)
    # except(TypeError, ValueError):
    #     raise HTTPException(
    #         status_code= status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid or expired token",
    #         headers={"WWW-Authenticate:": "Bearer"}
    #     )

    # #look up the user within the database
    # result = await db.execute(
    #     select(model.User)
    #     .where(model.User.id == user_id_int)
    # )

    # user = result.scalars().first()
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="User not found",
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )
    # return user
    #changed to current_user version
    return current_user

#Route to response GET request specific/individual user 
@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):

    #Build and runs a SQL query to check where user_id exist
    result = await db.execute(
        select(model.User)
        .where(model.User.id == user_id)
    )

    #get the first user object from the database if there exist an user else raise 404 Error
    user = result.scalars().first()

    if user:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


#Route/endpoints to response to the GET request for all the posts by a specific user
@router.get("/{user_id}/posts", response_model=PaginatedPostsResponse)
async def get_user_posts(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    #check if the user exist
    result = await db.execute(
        select(model.User)
        .where(model.User.id == user_id)
        .order_by(model.Post.date_posted.desc())
    )
    
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    #querry all the posts per user and return them --> need selectinload
    result = await db.execute(
        select(model.Post)
        .options(selectinload(model.Post.author))
        .where(model.Post.user_id== user_id)
    )
    posts = result.scalars().all()
    return posts


#Route/endpoints to response to the UPDATE request for their own profile's username, email and profile picture name
#update to only auhtorized user can edit their own profle
@router.patch("/{user_id}", response_model=UserPrivate)
async def update_user(
    user_id: int, 
    user_update: UserUpdate,
    current_user:CurrentUser, 
    db: Annotated[AsyncSession, Depends(get_db)]):

    #add ownership check of current_user
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    result = await db.execute(
        select(model.User)
        .where(model.User.id == user_id)
    )
    user = result.scalars().first()
    #check if the user exist to update else return 404 status
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    #check if the updated username the same as current username 
    #if different, check if there is other same username as updated one in database
    if user_update.username.lower() is not None and user_update.username.lower() != user.username.lower():
        result = await db.execute(
            select(model.User)
            .where(func.lower(model.User.username) == user_update.username.lower()
            )
        )
    
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    if user_update.email.lower() is not None and user_update.email.lower() != user.email.lower():
        result = await db.execute(
            select(model.User)
            .where(func.lower(model.User.email) == user_update.email.lower()
            )
        )
        
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    #UPDATE logic using setattr()
    update_data = user_update.model_dump(exclude_unset=True)

    # #loop over Python dict("username": "new_username")
    # for field, value in update_data.items():
    #     #setattr() --> for the user, set field(username) to the value(new_username)
    #     setattr(user, field, value)
    # UPDATE logic using manual condition statement
    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email.lower()

    #commit to the database after PUT opereation
    #no need to use db.add() because this is not insertion which require building new object
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, current_user:CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    #add ownership check 
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )   

    result = await db.execute(
        select(model.User)
        .where(model.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    old_filename = user.image_file
    #because db.delete() interact with the database session so need await
    await db.delete(user)
    await db.commit()#Route to response GET request specific/individual user 

    if old_filename:
        delete_profile_image(old_filename)

#----------------Profile Picture-------------------
#update profile picture
@router.patch("/{user_id}/picture", response_model=UserPrivate)
async def upload_profile_picture(
    user_id: int,
    file: UploadFile,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    #HTTP_403_FORBIDDEN: i know exactly who you are, but you are not allowed to do this
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's picture"
        )
    
    #Read the file(in byte)
    content = await file.read()

    #check the picture size
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {settings.max_upload_size_bytes // (1024 * 1024)}MB"
        )
    
    """
    image processing with Pillow is CPU bounded. If it is performed diretly in the asynchornous endponts
    it will block the await event loop. Therefore, run_in_threadpool() is needed to offload the CPU-bounded tasks
    on a worker thread. This will allow the event loop stays free to handle otther requests(maintain asynchornous)
    """

    #handle if the file is not an image 
    #this is handled since the content type from user upload might not be an image type --> use Pillow to validate it 
    try:
        new_filename = await run_in_threadpool(process_profile_image, content)
    except UnidentifiedImageError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file. Please upload a valid image(JPEG, PNG, GIF, WebP)."
        ) from err

    """
    Swap older picture with new one in order, so an user is never left with a broken profile 
    Current image is already been saved by the process_profile_image as `filename`.
    if we commit the old picture first and the commit() function then loose the user picture entirely
    """
    #save the old filename within the database(image_file is defined field within the db model)
    old_filename = current_user.image_file

    #update the database with the new filename
    current_user.image_file = new_filename

    #only after successful commit we will delete the old profile image 
    await db.commit()
    await db.refresh(current_user)

    if old_filename:
        delete_profile_image(old_filename)

    return current_user

    
#delete profile picture
@router.delete("/{user_id}/picture", response_model=UserPrivate)
async def delete_user_picture(
    user_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    #check the current user is authorized
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )

    #store the current old filename in the database with the same reason above
    old_filename = current_user.image_file

    #check if the current user have a picture to delete 
    if old_filename is None:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail="No picture to delete"
        )

    #return the default image path on the db and commit it before delete it on the disk
    current_user.image_file = None
    await db.commit()
    await db.refresh(current_user)

    delete_profile_image(old_filename)

    return current_user