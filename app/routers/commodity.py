from fastapi import Depends, APIRouter, Security
from sqlalchemy.orm import Session
from typing import List
from ..authorization.auth import auth_handler
from ..database import get_session
from ..models import Commodity, Simulation, get_current_user
from ..schemas import CommodityBase

router = APIRouter(prefix="/commodity", tags=["Commodity"])

@router.get("/", response_model=List[CommodityBase])
def get_commodities(
    db: Session = Depends(get_session),
    username=Depends(auth_handler.auth_wrapper)    
):
    """Get all commodities in the simulation of the logged-in user.
       
        Return a list of all commodities in the simulation of the user 
        making this request.     
    
        Return empty list if the user doesn't have a simulation yet.
    """

    u=get_current_user(username,db)
    simulation_id:Simulation=u.current_simulation_id

    if simulation_id == 0:
        return []
    commodities = db.query(Commodity).where(Commodity.simulation_id == simulation_id)
    return commodities

@router.get("/{id}",response_model=CommodityBase)
def get_commodity(
    id: str, 
    db: Session = Depends(get_session)):
    username=Depends(auth_handler.auth_wrapper)    

    """Get one commodity defined by id.
    Calls auth_wrapper to authorize access but does not use it to locate the user
    or the simulation, because id is unique to the whole app.

      Returns the commodity if it exists.

      Returns None if it does not exist.
    """

    commodity = db.query(Commodity).filter(Commodity.id == int(id)).first()
    return commodity
