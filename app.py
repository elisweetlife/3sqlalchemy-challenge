import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from flask import Flask, jsonify

###########################
# Data Base setup
###########################
engine = create_engine("sqlite:///hawaii.sqlite")

#Reflect the existing database into a new model
Base = automap_base()

##Reflect the tables
Base.prepare(engine, reflect=True)

#Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create our session (link) from Python to the DB
session = Session(engine)

###########################
app = Flask(__name__)

###########################
# Flask Routes
###########################

@app.route("/")
def welcome():
    return(
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Return the precipitations data fo the last year
    #Calculate the data 1 year ago from last date in database
    prev_year = dt.date(2017, 8,23) - dt.timedelta(days=365)

    #Query for the date and precipitation fo the last year
    #BADprecipitation = session.query(Measurement.date, Measurement.prcp)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
        

    precip = {date: prcp for date, prcp in precipitation}    
    return jsonify(precip)

        #filter(Measurement.station == 'USC00519281').\
        #filter(Measurement.date >= prev_year).all()

        #results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year)


@app.route("/api/v1.0/stations")
def stations():
    #Return a list of stations.
    results = session.query(Station.station).all()

    #unragel results into a 1D arrawy and convert to a list
    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    #Return temperature observations (tobs) for previous year
    #Calculate the date 1 year ago from last date in db
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #Query the primary station for all the tobs from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    #Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))

    #return the results
    return jsonify(temps)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    #Retrun TMIN, TAVG, TMAX.

    #Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # Calculate TMIN, TAVG, TMAX for dates greater than start date.
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()

        #Unravel results into a 1D and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)
