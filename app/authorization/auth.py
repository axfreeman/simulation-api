from asyncio import log
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader, APIKeyQuery, HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Security, status
from app.config import ALGORITHM, SECRET_KEY, API_KEY

class AuthHandler():
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password_hash(self, password)->str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id)->str:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=5),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            key=SECRET_KEY,
            algorithm=ALGORITHM
        )

    def decode_token(self, token):
        print(f"Decoding the token \n{token}")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            print(f"payload sub is {payload["sub"]}")
            return payload['sub']
        except JWTError as e:
            print(1,f"Could not validate token because {e}")
            raise HTTPException(status_code=401, detail=f'Could not validate token because {e}')

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)
    
auth_handler = AuthHandler()


"""The API key endpoints provide an administrator with a backdoor for
user information. 

This needs some minimal security protection.

However admins should not need to log in like a normal user.

So instead, we manually give them a key, on request.
"""
api_key_query = APIKeyQuery(name="api-key", auto_error=False)
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
) -> str:
    """Retrieve and validate an API key from the query parameters or HTTP header.

        api_key_query: The API key passed as a query parameter.
        api_key_header: The API key passed in the HTTP header.

        Returns the validated API key;
        Raises HTTPException if the API key is invalid.
    """
    if api_key_query == API_KEY:
        return api_key_query
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
    )

