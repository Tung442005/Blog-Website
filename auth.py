from datetime import UTC, datetime, timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from config import settings

#create password hasher using Argon2 with recommended default setting  --> no need to manually configure them
password_hash = PasswordHash.recommended()


#side effect: create Authentiation butto#extract the authetnication token's header when the client send itn in api/docs make the auth testing easier
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
        
