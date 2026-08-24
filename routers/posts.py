from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import model
from database import get_db
from schemas import PostCreate, PostResponse, PostUpdate

router = APIRouter()



# Route to respond to GET requests from the client at /api/posts
@router.get("", response_model=list[PostResponse])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(model.Post)
        .options(selectinload(model.Post.author))
        #we are give the descendending order of the querry(router) instead of the data itself
        .order_by(model.Post.date_posted.desc())
    )
    posts = result.scalars().all()
    # FastAPI automatically serialize the author - post relationship as the user response 
    return posts


#Route to reponse with the CREATE method 
@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(model.User).where(model.User.id == post.user_id),
    )
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
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"])
    return new_post

#Route response a single post request
@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):

    #Build and runs a SQL query to check where post_id exist
    result = await db.execute(
        select(model.Post)
        .options(selectinload(model.Post.author))
        .where(model.Post.id == post_id))

    #get the first user object from the database if there exist an user else raise 404 Error
    post = result.scalars().first()

    if post:
        return post 
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")




#Route/endpoints to response to the UPDATE request for single posts
#PUT --> full update
@router.put("/{post_id}", response_model=PostResponse)
async def update_post_full(post_id: int, post_data: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(model.Post)
        .options(selectinload(model.Post.author))
        .where(model.Post.id == post_id)
    )
    post = result.scalars().first()

    #check if the post exist to update --> else 404 error
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post was not found")

    #Check if the client is reassigning the existing post's author,
    #verify the new data contain user_id exists before allowing the update
    if post_data.user_id != post.user_id:
        result = await db.execute(
            select(model.User)
            .where(model.User.id == post_data.user_id))
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
    await db.commit()
    await db.refresh(post)
    return post


#PATCH --> partial update
@router.patch("/{post_id}", response_model=PostResponse)
async def update_post_partial(post_id: int, post_data: PostUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(model.Post)
        .options(selectinload(model.Post.author))
        .where(model.Post.id == post_id))
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
    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post

#Route/endpoint to handle DELETE request
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(model.Post)
        .options(selectinload(model.Post.author))
        .where(model.Post.id == post_id))
    post = result.scalars().first()
    #check if the post exist to DELETE --> else 404 error
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post was not found")

    await db.delete(post)
    await db.commit()