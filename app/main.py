from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.schemas import UserMessage, ServerMessage
from .database import Base, engine, get_session
from .authorization.auth import auth_handler, get_api_key
from .models import User
from .config import ALGORITHM, SECRET_KEY, SQLALCHEMY_DATABASE_URL

from .routers import (
    actions,
    commodity,
    simulation,
    user,
    admin,
    industry,
    socialClass,
    stocks,
    tests,
    trace
)

app=FastAPI()

users = []

Base.metadata.create_all(bind=engine)

@app.post("/register", status_code=201,response_model=UserMessage)
def register(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
)->str:
    """Register a new user

        form_data: user and password validated by OAuth2 middleware.

        Return status 400 for malformed form.
        
        Return status 400 if user already exists.
        
        Return status 201 if the user is registered.
    """

    if session.query(User).where(User.username == form_data.username).first() is not None:
        raise HTTPException(status_code=400, detail='Username is taken')
    user:User=User(
        username=form_data.username,
        password=auth_handler.get_password_hash(form_data.password),
        current_simulation_id=0
    )
    session.add(user)
    session.commit()
    return {'message': f'User {form_data.username} registered'}


@app.post('/login',status_code=200)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session))->dict:
    """Log a user in from credentials supplied in an OAuth2 form.

        form_data: user and password, validated by OAuth2 middleware.

        Return status 400 for malformed form.

        Return status 200 and supply a token if login succeeds.
    """
    user:User=session.query(User).where(User.username == form_data.username).first()

    if user is None:
        raise HTTPException(status_code=401, detail=f'User {form_data.username} does not exist')
    else:
        print(f"Verifying password for user {user.username} with supplied password {form_data.password} and stored password {user.password}")
        try:
            if not auth_handler.verify_password(form_data.password, user.password):
                raise HTTPException(status_code=401, detail='Invalid username and/or password')
        except Exception as e: # If there's a problem, bcrypt throws an exception. This way, we don't have to plough through a traceback
                raise HTTPException(status_code=401, detail=f'Password validation error {e}')

    session.add(user)

    # TODO does the server actually need to keep track of whether the user is logged in or not?
    user.is_logged_in=True
    session.commit()
    token = auth_handler.encode_token(user.username)
    print(f"Returning the token \n{token}\n")
    return {"token":token}

app.include_router(actions.router)
app.include_router(simulation.router)
app.include_router(commodity.router)
app.include_router(user.router)
app.include_router(admin.router)
app.include_router(industry.router)
app.include_router(socialClass.router)
app.include_router(stocks.router)
app.include_router(trace.router)
# app.include_router(tests.router)
