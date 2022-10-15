import datetime as dt
import numpy as np
import pandas as pd


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

###########  The following code is nearly identical to Day 3 Activity 10 
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
###### Everything you need here can be found in Day 3 Activity 10
@app.route("/")
def welcome():
    return (
    f"Available Routes:<br/>" 
    f"/api/v1.0/precipitation<br/>" 
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/temp/<start><br/>"
    f"/api/v1.0/temp/<start>/<end>"
    
    )
recent_date = session.query(func.max(measurement.date)).first()[0]
###### the 'precipitation' route you will query and return the data Day 3 Activity 10
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database
    recent_date = session.query(func.max(measurement.date)).first()[0]
    
    
    # Query for the date and precipitation for the last year
    one_year = dt.datetime.strptime(recent_date,"%Y-%m-%d") - dt.timedelta(days=365)
    one_year_str = one_year.strftime("%Y-%m-%d")
    one_year_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_str).all()
    session.close()
   
    # # Dict with date as the key and prcp as the value
    prcp_dict = []
    for date, prcp in one_year_data:
        date_dict = {}
        date_dict["Date"] = date
        date_dict["Precipitation"] = prcp
        prcp_dict.append(date_dict)
    
        
    return jsonify(prcp_dict)


###### the 'stations' route you will query and return the data Day 3 Activity 10
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Unravel results into a 1D array and convert to a list
    results = session.query(station.name).all()
    session.close()

    return jsonify(list(np.ravel(results)))

###### the 'tobs' route you will query and return the data Day 3 Activity 10
@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations (tobs) for previous year."""
    session = Session(engine)
    # Calculate the date 1 year ago from last date in database
    one_year = dt.datetime.strptime(recent_date,"%Y-%m-%d") - dt.timedelta(days=365)
    one_year_str = one_year.strftime("%Y-%m-%d")

    # Query the primary station for all tobs from the last year
    most_active = session.query(measurement.station, func.count()).group_by(measurement.station).order_by(func.count().desc()).all()[0][0]
    one_year_tobs = session.query(measurement.date, measurement.tobs).filter(measurement.date >= one_year_str, measurement.station==most_active).all()
    session.close()
    
    # Unravel results into a 1D array and convert to a list
    # Return the results
    return jsonify(list(np.ravel(one_year_tobs)))
    

###### the 'temp' route you will query the data with params in the url and return the data Day 3 Activity 10
@app.route("/api/v1.0/temp/<sdate>")
def startdate(sdate):
    """Return TMIN, TAVG, TMAX."""
    session = Session(engine)
    one_year_tobs = session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.date >=sdate).group_by(measurement.date).all()
       # # Dict with date as the key and prcp as the value
    # startdate_dict = {}
    # for data in one_year_tobs:
    #    startdate_dict[data[0]]={'min':one_year_tobs[1], 'max':one_year_tobs[2], 'avg':one_year_tobs[3] }
    data_list = []
    for result in one_year_tobs:
        row = {}
        row['Start Date'] = result[0]
        row['Lowest Temperature'] = float(result[1])
        row['Highest Temperature'] = float(result[2])
        row['Average Temperature'] = float(result[3])
        data_list.append(row)
             
    
    return jsonify(data_list) 


@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
    session = Session(engine)
    one_year_tobs = session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.date >=start, measurement.date <=end).group_by(measurement.date).all()
    data_list = []
    for result in one_year_tobs:
            row = {}
            row['Start Date'] = result[0]
            row['Lowest Temperature'] = float(result[1])
            row['Highest Temperature'] = float(result[2])
            row['Average Temperature'] = float(result[3])
            data_list.append(row)

    return jsonify(data_list) 
#     # Select statement
#     # calculate TMIN, TAVG, TMAX with start and stop
#     if end is not None:
#         results = session.query(func.min(measurement.tobs),
#         func.avg(measurement.tobs),
#         func.max(measurement.tobs),
#         ).filter(measurement.date>start, measurement.date<end).all()[0]
#     else:
#         results = session.query(func.min(measurement.tobs),
#         func.avg(measurement.tobs),
#         func.max(measurement.tobs),
#         ).filter(measurement.date>start).all()[0]
#     TMIN = results[0]
#     TAVG = results[1]
#     TMAX = results[2]

#     # Unravel results into a 1D array and convert to a list
#     return jsonify([TMIN, TAVG, TMAX])


if __name__ == "__main__":
    app.run(debug=True)
