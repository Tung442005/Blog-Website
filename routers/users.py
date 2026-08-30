from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import model
from auth import (
    create_access_token, 
    hash_password, 
    verify_access_token, 
    verify_password
)
from database import get_db
from schemas import UserCreate, UserPublic, UserPrivate, Token, UserUpdate, PostResponse

from config import settings

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





#Route to response GET request specific/individual user 
@router.get("/{user_id}", response_model=UserResponse)
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
@router.get("/{user_id}/posts", response_model=list[PostResponse])
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


#Route/endpoints to response to the UPDATE request for single posts
@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
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
    if user_update.username is not None and user_update.username != user.username:
        result = await db.execute(
            select(model.User)
            .where(model.User.username == user_update.username)
        )
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    if user_update.email is not None and user_update.email != user.email:
        result = await db.execute(
            select(model.User)
            .where(model.User.email == user_update.email))
        
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
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(model.User)
        .where(model.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    #because db.delete() interact with the database session so need await
    await db.delete(user)
    await db.commit()#Route to response GET request specific/individual user 

