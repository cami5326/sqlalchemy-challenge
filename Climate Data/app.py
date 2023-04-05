#import the dependencies
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import pandas as pd
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#reflect an existing database into a new model
Base = automap_base()
#reflect the tables
Base.prepare(autoload_with=engine)

#save references to each table
foundClassesMeasurement = Base.classes.measurement
foundClassesStation = Base.classes.station

#create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
#homepage route with all the available routes
@app.route("/")
def home():
    print("Server attempted to go to home page...") #print in output console in python
    return (f"Welcome to the Climate App API page. This is the homepage.<br>"
            f"Current routes:<br>"
            f"/<br>"
            f"/api/v1.0/precipitation<br>"
            f"/api/v1.0/stations<br>"
            f"/api/v1.0/tobs<br>"
            f"/api/v1.0/start<br>"
            f"/api/v1.0/start/end<br>"
            )  #prints in the browser

#precipitation route with the last 12 months of precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    datesQuery = session.query(foundClassesMeasurement.date,foundClassesMeasurement.prcp).filter(foundClassesMeasurement.date >= (dt.date(2017,8,23) - dt.timedelta(days=365))).all() 
    df = pd.DataFrame(datesQuery)
    dfdic = df.to_dict(orient='records')
    return jsonify(dfdic)

#stations route with the list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stationQuery = session.query(foundClassesMeasurement.station).distinct().all()
    stationQuerydf = pd.DataFrame(stationQuery)
    stationQuerydfdic = stationQuerydf.to_dict(orient='records')
    return jsonify(stationQuerydfdic)

#temperature route with the the dates and temperature observations of the most-active station for the previous year of data
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    mostStation = session.query(foundClassesMeasurement.date,foundClassesMeasurement.tobs
                           ).filter(foundClassesMeasurement.date >= (dt.date(2017,8,23) - dt.timedelta(days=365))
                                   ).filter(foundClassesMeasurement.station == 'USC00519281').all()
    mostStationdf = pd.DataFrame(mostStation)
    mostStationdfdic = mostStationdf.to_dict(orient='records')
    return jsonify(mostStationdfdic)

#start date route
@app.route("/api/v1.0/<start>")
def start(start=None):
    session = Session(engine)
    mostStationTemp = session.query(func.min(foundClassesMeasurement.tobs
                            ),func.max(foundClassesMeasurement.tobs
                                ),func.avg(foundClassesMeasurement.tobs)).filter(foundClassesMeasurement.date >= (start)).all()
    
    mostStationTempunravel = list(np.ravel(mostStationTemp))
    return jsonify (mostStationTempunravel) 

#start and end date route
@app.route("/api/v1.0/<start>/<end>")
def both(start=None, end=None):
    session = Session(engine)
    mostStationTemp = session.query(func.min(foundClassesMeasurement.tobs
                            ),func.max(foundClassesMeasurement.tobs
                                ),func.avg(foundClassesMeasurement.tobs)).filter((foundClassesMeasurement.date >= start) & (foundClassesMeasurement.date <= end)).all()
    
    mostStationTempunravel = list(np.ravel(mostStationTemp))
    return jsonify (mostStationTempunravel) 

#default name of the application so we can start it from our command line
if __name__ == "__main__":
    app.run(debug=True) # module used to start the development server
        