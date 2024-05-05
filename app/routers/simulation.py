import http
from fastapi import  HTTPException, Security, status, Depends, APIRouter,status
from sqlalchemy.orm import Session
from typing import List
from ..reporting.caplog import logger
from ..database import  get_session
from ..models import Simulation, User
from ..schemas import  SimulationBase
from ..authorization.auth import get_api_key

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

@router.get("/",response_model=List[SimulationBase])
def get_simulations(
    session: Session = Depends (get_session), 
    u:User=Security(get_api_key),    
    ):    
    """Get all simulations belonging to one user.

        Return all simulations belonging to the user 'u'
        If there are none, return an empty list.
    """        
    simulations = session.query(Simulation).where(Simulation.username == u.username)
    return simulations

@router.get("/by_id/{id}",response_model=SimulationBase)
def get_simulation(
    id:str,
    u:User=Security(get_api_key),    
    session: Session=Depends(get_session)):    
    
    """Get one simulation.
        
        id is the actual simulation number.
        
        Raise httpException if there is no such simulation
    """
    simulation=session.query(Simulation).filter(Simulation.id==int(id)).first()
    if simulation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='This simulation does not exist')
    return simulation

@router.get("/current",response_model=List[SimulationBase])
def get_current_user_simulation(
    session: Session = Depends (get_session), 
    u:User=Security(get_api_key),    
    ):

    """Get the current simulation of the api_key user
    
        Return the user's current simulation if there is one.

        Raise httpException otherwise
    """
    logger.info(f"User {u.username} requested simulation {u.current_simulation_id}")
    simulations:Simulation=session.query(Simulation).where(Simulation.id==u.current_simulation_id)
    if simulations is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='This user has no simulations')
    return simulations


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
