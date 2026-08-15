from __future__ import annotations
from datetime import UTC, datetime

from sqlalchemy import ForeignKey, DateTime, Integer, String, Text 
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

#User model

class User(Base):
    #table name
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    #Only store the file name to our images --> not gonna store the entire path
    """
    It helps decoupling/seperate our database from the file structure 
    --> if we reorganize our files by changing or renaming directories, we dont need to update the database since 
    every single row in the database referencing an image is now wrong if we use the full path 
    We could just change that in one place --> helpful for migration 

    Mapped[str | None] tell this is an optional field
    """
    image_file: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        default=None
    )

    """
    This one-to-many relationship setup is pire Python/ORM convenience, neither exists as an actual
    column in either table. The real database schema only contains what we've defined so far
    """
    posts : Mapped[list[Post]] = relationship(back_populates="author")

    #@property is the bulit-in Python decrorator turning methods into something accessed like an attribute, not called like function
    @property
    #also not a DB column stuff just python ORM
    def image_path(self) -> str:
        #refers back to the DB column we defined earlier 
        if self.image_file:
            #customer upload customized image 
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"


class Post(Base):
        __tablename__ = "posts"

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        title: Mapped[str] = mapped_column(Integer, unique=True, nullable=False)
        content: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
        user_id: Mapped[str] = mapped_column(
             ForeignKey("users.id"),
             nullable=False,
             #faster read --> slower write and more storage
             index=True
        )
        #define timestamp when a post is created 
        date_posted: Mapped[datetime] = mapped_column(
             #tell the database to store timezone-aware datetimes 
             DateTime(timezone=True), 
             #default value if clien does not explicitly provide it 
             default=lambda: datetime.now(UTC)

        )

        #many-to-one relationship
        author : Mapped[User] = relationship(back_populates="posts")