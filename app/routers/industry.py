from typing import List
from fastapi import Security, Depends, APIRouter
from sqlalchemy.orm import Session
from ..authorization.auth import auth_handler
from ..database import get_session
from ..models import Simulation, Industry, get_current_user
from ..schemas import IndustryBase

router = APIRouter(prefix="/industry", tags=["Industry"])

@router.get("/", response_model=List[IndustryBase])
def get_Industries(
    session: Session = Depends(get_session),
    username:str = Depends(auth_handler.auth_wrapper)):
    
    """Get all industries in the simulation of the logged-in user
    Return empty list if the user doesn't have a simulation yet.
    """
    
    u=get_current_user(username,session)
    simulation_id:Simulation=u.current_simulation_id
    if simulation_id == 0:
        return []
    Industries = session.query(Industry).where(Industry.simulation_id == simulation_id)
    return Industries

@router.get("/{id}", response_model=IndustryBase)
def get_Industry(
    id: str, 
    session: Session = Depends(get_session),
    username:str = Depends(auth_handler.auth_wrapper)
    ):

    """Get one industry defined by id.
    Calls auth_wrapper to authorize access but does not use it to locate
    the user or the simulation, because id is unique to the whole app.

      Returns the industry if it exists.

      Returns None if it does not exist.
    """
    
    Industry = session.query(Industry).filter(Industry.id == int(id)).first()
    return Industry
