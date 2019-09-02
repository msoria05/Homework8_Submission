import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, inspect

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#  Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart_date_as_YYYY-MM-DD&gt:&ltend_date_as_YYYY-MM-DD&gt<br/>"
        f"/api/v1.0/&ltstart_date_as_YYYY-MM-DD&gt<br/>"
    )


# PRECIPITATION
@app.route("/api/v1.0/precipitation")
def precipitation():

    print("The precipitation for the last year of data:")

    # Query to find last date using "Measurement" class
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_date[0]

    # Calculate the date 1 year ago from the last data point in the database
    prior_year_date = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=366)
    
    # Perform a query to retrieve the data and precipitation scores
    results_precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prior_year_date).all()

    # Convert the query results to a Dictionary
    precipitation_dict = dict(results_precipitation)
    
    # Return the JSON representation
    return jsonify(precipitation_dict)


# STATIONS
@app.route("/api/v1.0/stations")
def stations():
   
    # Query stations
    stations = (session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all())
    
    # Convert to list: https://docs.scipy.org/doc/numpy/reference/generated/numpy.ravel.html
    station_list = list(np.ravel(stations))

    # Return a JSON list of stations
    return jsonify(station_list)    


# TEMPERATURES
@app.route("/api/v1.0/tobs")
def temperature():
    
    # Query to find last date using "Measurement" class
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_date[0]

    # Calculate the date 1 year ago from the last data point in the database
    prior_year_date = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=366)

    # Query for the dates and temperature observations from a year from the last data point.
    temp_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= prior_year_date).all()

     # Convert to list: https://docs.scipy.org/doc/numpy/reference/generated/numpy.ravel.html
    temp_list = list(np.ravel(temp_data))
    
    # Return a JSON list of Temperature Observations (tobs) for the previous year
    return jsonify(temp_list)


# START DATE AND END DATE (RANGE)
@app.route("/api/v1.0/<start>:<end>")
def start_end(start=None, end=None):
    
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()

    # Convert to list: https://docs.scipy.org/doc/numpy/reference/generated/numpy.ravel.html
    between_dates_list=list(between_dates)
    
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end date range.
    return jsonify(between_dates_list)

# START DATE ONLY
@app.route("/api/v1.0/<start>")
def start(start=None):

    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    
    # Convert to list: https://docs.scipy.org/doc/numpy/reference/generated/numpy.ravel.html
    from_start_list=list(np.ravel(from_start))

    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.
    return jsonify(from_start_list)

if __name__ == '__main__':
    app.run(debug=True)