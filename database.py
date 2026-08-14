from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

#build objet that manage the actual connectio to the database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread":False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#share parent class for futre ORM models 
#inheriting from Base is what lets SQLAlchemy discover and map current Class to an actual Table nbnbnbnb
class Base(DeclarativeBase):
    pass

#use generator
def get_db():
    with SessionLocal() as db:
        yield db