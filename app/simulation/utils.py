from ..models import Class_stock, Commodity,Industry, Industry_stock, Simulation
from app.logging import report
from sqlalchemy.orm import Session

"""Helper functions for use in all parts of the simulation."""

def revalue_commodities(
      session:Session, 
      simulation:Simulation):
  """Calculate the size, value and price of all commodities from their stocks
  Recalculate unit values and unit prices on this basis.

  Normally, 'revalue stocks' should be called after this, because a change
  in the unit value and/or price will affect all stocks of it.

      session(Session):
          The sqlAlchemy session which will commit the commodity to storage

      simulation(Simulation):
          The simulation to which this calculation refers
  """

  report(1,simulation.id,"CALCULATE THE SIZE, VALUE AND PRICE OF ALL COMMODITIES",session)
  commodities=session.query(Commodity).where(Commodity.simulation_id==simulation.id)
  for commodity in commodities:
      commodity.total_value=0
      commodity.total_price=0
      commodity.size=0
      session.add(commodity)

# Industry stocks
      istocks=session.query(Industry_stock).where(Industry_stock.commodity_id==commodity.id)
      for stock in istocks:
          commodity.total_value+=stock.value
          commodity.total_price+=stock.price
          commodity.size+=stock.size

# Class stocks
      cstocks=session.query(Class_stock).where(Class_stock.commodity_id==commodity.id)
      for stock in cstocks:
          commodity.total_value+=stock.value
          commodity.total_price+=stock.price
          commodity.size+=stock.size
  session.commit()

  for commodity in commodities:
      if commodity.size>0:
        commodity.unit_price=commodity.total_price/commodity.size
        commodity.unit_value=commodity.total_price/commodity.size
        report(2,simulation.id,f"Setting the size of commodity {commodity.name} to {commodity.size}",session)
        report(2,simulation.id,f"Setting the value of commodity {commodity.name} to {commodity.total_value} and its price to {commodity.total_price}",session)
        report(2,simulation.id,f"Setting the unit value of commodity {commodity.name} to {commodity.unit_value} and its unit price to {commodity.unit_price}",session)

def revalue_stocks(db:Session, simulation:Simulation):
  """ Interrogate all stocks.
  Set value from unit value and size of their commodity
  Set price from unit price and size of their commodity
  """
  report(1,simulation.id,"RESETTING PRICES AND VALUES",db)

# Industry stocks

  istocks=db.query(Industry_stock).where(Industry_stock.simulation_id==simulation.id)
  report(2,simulation.id,"Revaluing industry stocks",db)
  for stock in istocks:
      commodity=db.query(Commodity).where(Commodity.id == stock.commodity_id).first()
      db.add(stock)
      stock.value=stock.size*commodity.unit_value
      stock.price=stock.size*commodity.unit_price
      report(3,simulation.id,f"Setting the value of the stock [{stock.name}] to {stock.value} and its price to {stock.price}",db)
  db.commit()

# Class stocks

  cstocks=db.query(Class_stock).where(Class_stock.simulation_id==simulation.id)
  report(2,simulation.id,"Revaluing class stocks",db)
  for stock in cstocks:
      commodity=db.query(Commodity).where(Commodity.id == stock.commodity_id).first()
      db.add(stock)
      stock.value=stock.size*commodity.unit_value
      stock.price=stock.size*commodity.unit_price
      report(3,simulation.id,f"Setting the value of the stock [{stock.name}] to {stock.value} and its price to {stock.price}",db)
  db.commit()

def calculate_capital(db:Session, simulation:Simulation,industry:Industry)->float:
    """
    Calculate the initial capital of the given industry and return it
    This is equal to the sum of the prices of all its stocks
    Assumes that the price of all these stocks has been set
    """
    report(2,simulation.id,f"Calculating the capital of {industry.name}",db)
    result=0
    istocks=db.query(Industry_stock).where(Industry_stock.industry_id==industry.id)
    for stock in istocks:
        report(3,simulation.id,f"Industry stock [{stock.name}] is adding {stock.price} to the capital of {industry.name}",db)
        result+=stock.price
    return result

def calculate_initial_capitals(db:Session, simulation:Simulation):
    """
    Calculate the initial capital of the given industry and return it
    This is equal to the sum of the prices of all its stocks
    Assumes that the price of all these stocks has been set correctly
    """
    report(1,simulation.id,f"CALCULATING INITIAL CAPITAL for simulation {simulation.id}",db)
    industries=db.query(Industry).where(Industry.simulation_id==simulation.id)
    for industry in industries:
      report(2,simulation.id,f"Asking for the capital of {industry.name}",db)      
      db.add(industry)
      industry.initial_capital=calculate_capital(db,simulation,industry)
    db.commit()

def calculate_current_capitals(db:Session, simulation:Simulation):
    """
    Calculate the current capital of all industries in the simulation.
    Set the profit and the profit rate of each industry.
    Assumes that the price of all stocks has been set correctly.
    """
    report(1,simulation.id,"CALCULATING CURRENT CAPITAL",db)
    industries=db.query(Industry).where(Industry.simulation_id==simulation.id)
    for industry in industries:
      db.add(industry)
      industry.current_capital=calculate_capital(db,simulation,industry)
      industry.profit=industry.current_capital-industry.initial_capital
      industry.profit_rate=industry.profit/industry.initial_capital
    db.commit()


