from datetime import UTC, datetime, timedelta
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from config import settings
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
import model

 

#create password hasher using Argon2 with recommended default setting  --> no need to manually configure them
password_hash = PasswordHash.recommended()


#side effect: create Authentiation button and extract the token from authorization header(a line in http request) when the client send itn in api/docs make the auth testing easier
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")

#hash_password function
def hash_password(password: str) -> str:
    return password_hash.hash(password)

#verify if the plain password match the hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

#create access token
#store user_id in sub field and pass the dict
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    #ensure the orginal dict does not cahnge
    to_encode = data.copy()
    #manually set lifetime for a token
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    #default lifetime
    else: 
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    #add dealine to the payload as {"exp": expire}
    to_encode.update({"exp": expire})
    #create access token
    encoded_jwt = jwt.encode(
        to_encode, 
        #get actual string from config.py for the token's signature
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm
    )

    return encoded_jwt

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


async def get_current_user( 
    token: Annotated[str, Depends(oauth2_scheme)], 
    db: Annotated[AsyncSession, Depends(get_db)]
) -> model.User:
    
    #check if current user have valid token(signed, unexpired, sub present) else return 401 error 
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate":"Bearer"}
        )
    """
    validate if the user_id is interger when it comes out of JWT payload(jwt decode) 
    when server receive request from client request with token
     --> payload["sub"]
    (sub present in the token must be integer)
    """
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    result = await db.execute(
        select(model.User).where(model.User.id == user_id_int)
    )
    #strip one-element row tuples to bare ORM objects then take the first one
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

#Explain: Reusable alias for currentuser parameter
#model.User reutrn the DB row
#Dpends(get_current_user)
"""
1. extract token (oauth2_scheme)
2. verify signature/expiry  → 401
3. int(sub) datatype check  → 401
4. fetch user from DB       → 401 if gone
5. return the User object
    """
CurrentUser = Annotated[model.User, Depends(get_current_user)]




    
    


