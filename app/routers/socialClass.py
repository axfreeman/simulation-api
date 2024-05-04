from typing import List
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from ..authorization.auth import auth_handler
from ..database import  get_session
from ..models import SocialClass,Simulation,get_current_user
from ..schemas import SocialClassBase

router=APIRouter(
    prefix="/classes",
    tags=['Class']
)

@router.get("/",response_model=List[SocialClassBase])
def get_socialClasses(
        db: Session = Depends (get_session),
        username:str = Depends(auth_handler.auth_wrapper)):

    """Get all social classes in the simulation of the logged-in user
    Return empty list if the user doesn't have a simulation yet.
    """

    u=get_current_user(username,db)
    simulation_id:Simulation=u.current_simulation_id
    if (simulation_id==0):
        return []
    socialClasses=db.query(SocialClass).where(SocialClass.simulation_id==simulation_id)
    return socialClasses

@router.get("/{id}")
def get_socialClass(
        id:str,db: 
        Session=Depends(get_session),
        username:str = Depends(auth_handler.auth_wrapper)):

    """Get one SocialClass defined by id.
    Calls auth_wrapper to authorize access but does not use it to locate the user
    or the simulation, because id is unique to the whole app.

      Returns the SocialClass if it exists.

      Returns None if it does not exist.
    """
    socialClass=db.query(SocialClass).filter(SocialClass.id==int(id)).first()
    return socialClass

