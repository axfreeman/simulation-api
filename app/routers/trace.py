from fastapi import  Depends, APIRouter, Security
from sqlalchemy.orm import Session
from typing import List
from ..authorization.auth import auth_handler
from ..database import  get_session
from ..models import Simulation,Trace,User,get_current_user
from ..schemas import TraceOut

router=APIRouter(
    prefix="/trace",
    tags=['Trace']
)

@router.get("/",response_model=List[TraceOut])
def get_trace(
    session: Session = Depends (get_session),
    username:str=Depends(auth_handler.auth_wrapper)):
    """Get all trace records in the simulation of the logged-in user
    Return empty list if the user doesn't have a simulation yet.
    """
    u:User=get_current_user(username,session)

    simulation_id:Simulation=u.current_simulation_id
    if (simulation_id==0):
        return []
    trace=session.query(Trace).where(Trace.simulation_id==simulation_id)
    return trace
