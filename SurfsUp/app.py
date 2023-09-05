# Import the dependencies.

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import numpy as np
import datetime as dt


#################################################
# Database Setup
#################################################

# create engine to hawaii.sqlite

engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(engine, reflect=True)

# Save references to each table

Measurement=Base.classes.measurement
Station=Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Homepage:

@app.route("/")
def home():
    
    return (f"<h1> <b> Welcome to the climate page <b/></h1>"
            F"<br/>"
            f"<ol>"
            f"<strong><h2> Available pages : </h2></strong><br/>"
            f"<li><h3>/api/v1.0/precipiation </h3><br/>"
            f"<li><h3>/api/v1.0/stations </h3><br/>"
            f"<li><h3>/api/v1.0/tobs </h3><br/>"
            f"<li><h3>/api/v1.0/temp/start</h3><br/>"
            f"<li><h3>/api/v1.0/temp/start/end</h3><br/>"
            f"<ol>"
            )

# Precipitation analysis:

@app.route("/api/v1.0/precipiation")
def precipitaion():
    session = Session(engine)
    previous_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    results = session.query(Measurement.date,Measurement.prcp).\
                filter(Measurement.date>=previous_year).all()
    session.close()
    previous_year_date_prcp_list = []
    for date, prcp in results:
        previous_year_date_prcp_dict = {}
        previous_year_date_prcp_dict["date"] = date
        previous_year_date_prcp_dict["prcp"] = prcp
        previous_year_date_prcp_list.append(previous_year_date_prcp_dict)
    return jsonify(previous_year_date_prcp_list)

# list of station names:

@app.route("/api/v1.0/stations")
def station_names():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    all_names = list(np.ravel(results))
    return jsonify (all_names)

# most-active stations:

@app.route("/api/v1.0/tobs")
def active_stations():
    session = Session(engine)
    previous_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    results=session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date>=previous_year).all()
    session.close()
    results = list(np.ravel(results))
    return jsonify (results)
    

# Return a JSON list of the TMIN,TAVG, TMAX for a specified start or start-end range.
    
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    
    # Select statement
    
    sel = [func.min(Measurement.tobs), 
           func.avg(Measurement.tobs), 
           func.max(Measurement.tobs)]
    
    if not end:
        
        start = dt.datetime.strptime(start,"%m%d%Y")
        
        # Compute TMIN, TAVG, TMAX for start date
        results = session.query(*sel).\
                        filter(Measurement.date >= start).all()
        session.close()
        
        # Unravel and convert to list
        temps = list(np.ravel(results))
        return jsonify (temps)
    
      # Compute TMIN, TAVG, TMAX with start and stop date
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    results = session.query(*sel).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()
    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

# Run the app.
    
if __name__ == "__main__":
    app.run(debug=True)
