from fastapi import  Security, status, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List
from ..authorization.auth import auth_handler
from ..logging import report
from ..database import  get_session
from ..models import Simulation, User, get_current_user
from ..schemas import  SimulationBase

"""Endpoints to retrieve data about Simulations.
At present these are all public.
This is because there is no privacy consideration.
Any user can see what any other is doing.
But each user can only *change* what that user is doing.
"""

router=APIRouter(
    prefix="/simulations",
    tags=['Simulation']
)

@router.get("/by_id/{id}",response_model=SimulationBase)
def get_simulation(
    id:str,
    session: Session=Depends(get_session)):    
    
    """Get one simulation.
        
        id is the actual simulation number.
        not normally accessed directly by the user.
        useful for client GUIs.
    """
    simulation=session.query(Simulation).filter(Simulation.id==int(id)).first()
    return simulation

@router.get("/mine",response_model=List[SimulationBase])
def get_simulations(
    session: Session = Depends (get_session), 
    username=Depends(auth_handler.auth_wrapper)):    
    """Replies with all simulations belonging to the logged-in user.

        Return all simulations belonging to the logged-in user
        If there are none, return an empty list.
    """        
    u:User=get_current_user(username,session)
    simulations = session.query(Simulation).where(Simulation.username == u.username)
    return simulations

@router.get("/current",response_model=SimulationBase)
def get_current_user_simulation(
    session: Session = Depends (get_session), 
    username=Depends(auth_handler.auth_wrapper)):

    """Get the current simulation belonging to the logged-in user.
    
        Return the user's current simulation if there is one.

        Return None otherwise.
    """

    u:User=get_current_user(username,session)
    simulation:Simulation=u.current_simulation(session)
    return simulation


# @router.get("/delete/{id}")
# def delete_simulation(id:str,session: Session=Depends(get_session),u:User=Depends(get_current_user))->str:    
#     """
#     Delete the simulation with this id and all dependent objects.

#         If the user has no such simulation, do nothing and return None
#         If the user does have this simulation, delete and return confirmation.
#     """
#     if u is None or u.current_simulation_id is None or u.current_simulation_id.state=="TEMPLATE": 
#         return None
#     print(f"{u.username} wants to delete simulation {u.current_simulation_id}")
#     if (u.current_simulation_id != None):
#        session.delete(u.current_simulation_id)

#     session.commit()
#     userMessage:str={"message":f"Simulation {id} deleted","statusCode":status.HTTP_200_OK}
#     return userMessage
