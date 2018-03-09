# coding utf8

import pandas as pd
import datetime
import distance

def importJson(filepath, addColumns=True) :

    # Loading data
    raw = pd.io.json.read_json(filepath)
    df = raw['locations'].apply(pd.Series)

    # Create latitude and longitude columns
    df['latitude'] = df['latitudeE7'] * 0.0000001
    df['longitude'] = df['longitudeE7'] * 0.0000001

     # Clean up columns
    columns = ["timestampMs", "latitude", "longitude"]
    for col in list(df) :
        if col not in columns :
            del df[col]

    # Add date column in format 'dd-mm-YY'
    dates = []
    for timestamp in df['timestampMs']:
        dates.append(datetime.datetime.fromtimestamp(int(timestamp) / 1000).strftime('%d-%m-%Y'))
    df['date'] = dates

    # Add time column in format 'HH:MM:SS'
    time = []
    for row in df['timestampMs']:
        time.append(datetime.datetime.fromtimestamp(int(row) / 1000).strftime('%H:%M:%S'))
    df['time'] = time

    if not addColumns :
        return df
    else :
        # Add delay column seconds
        delay = []
        delay.append(0)
        for i in range(df['timestampMs'].size - 1):
            delay.append(int(int(df['timestampMs'][i]) - int(df['timestampMs'][i + 1])) / 1000)
        df['delay'] = delay

        # Add distance, velocity and acceleration 
        df['distance'] = distance.getDistances(df)
        df['velocity'] = distance.getVelocities(df)
        df['acceleration'] = distance.getAccelerations(df)

        return df

def selectDate(date, df) :
    result = df[df['date'] == date]
    return result.reset_index(drop=True) # Reset indices of dataframe