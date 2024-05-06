# Import the dependencies.
import datetime as dt
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    return (
        f"Welcome to the Climate App!<br/>"
        f"Available Routes:<br/>"
        f"1. /api/v1.0/precipitation - Precipitation data for the last 12 months<br/>"
        f"2. /api/v1.0/stations - List of stations<br/>"
        f"3. /api/v1.0/tobs - Temperature observations for the last 12 months<br/>"
        f"4. /api/v1.0/start_date - Minimum temperature, average temperature, and maximum temperature for a specified start date<br/>"
        f"5. /api/v1.0/start_date/end_date - Minimum temperature, average temperature, and maximum temperature for a specified start and end date<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    
    
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    total_stations = session.query(Station.station, Station.name).all()
    stations_list = []
    
    for station, name in total_stations:
        stations_list.append({
            "station": station,
            "name": name
        })
    print(stations_list)
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    
    # most_active_station_id = most_active_stations[0][0]
    
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)
    
    temp_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= one_year_ago).all()
    
    temp_list = [{"data": date, "tobs": tobs} for date, tobs in temp_data]
    
    print("From line 88: ", temp_list)
    return jsonify(temp_list)


# /api/v1.0/<start> and  /api/v1.0/<start>/<end>
"""
Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a speciFed start or start-end range.

For a speciFed start, calculate TMIN , TAVG , TMAX for all the dates and greater than or equal to the start date.
 
For a speciFed start date and end date, calculate TMIN TAVG , and TMAX for the dates from the start date to the end date, inclusive
"""

@app.route("/api/v1.0/<start>")
def temp_range(start):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    
    print(temp_data)
    temp_dict = {
        "date": start_date,
        "min_temp": temp_data[0][0],
        "avg_temp": temp_data[0][1],
        "max_temp": temp_data[0][2]
    }
    return jsonify(temp_dict)


@app.route('/api/v1.0/<start>/<end>')
def temp_range_start_end(start, end):
    
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    temp_dict = {
        "start_date": start_date,
        "end_date": end_date,
        "min_temp": temp_data[0][0],
        "avg_temp": temp_data[0][1],
        "max_temp": temp_data[0][2]
    }
    
    return jsonify(temp_dict)

if __name__ == "__main__":
    app.run(debug=True)