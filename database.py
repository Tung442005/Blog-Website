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