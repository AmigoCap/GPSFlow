# coding utf8
import pandas as pd
import datetime
import distance

def importData(nameFile) :
    # Loading data
    raw = pd.io.json.read_json(nameFile)
    df = raw['locations'].apply(pd.Series)

    # Clean up columns
    del df['accuracy']
    del df['activity']
    del df['altitude']
    del df['velocity']
    del df['heading']

    df['latitude'] = df['latitudeE7'] * 0.0000001
    df['longitude'] = df['longitudeE7'] * 0.0000001

    del df['longitudeE7']
    del df['latitudeE7']

    dates = []
    for row in df['timestampMs']:
        dates.append(datetime.datetime.fromtimestamp(int(row) / 1000).strftime('%d-%m-%Y'))

    df['date'] = dates

    time = []
    for row in df['timestampMs']:
        time.append(datetime.datetime.fromtimestamp(int(row) / 1000).strftime('%H:%M:%S'))

    df['time'] = time

    delay = []
    delay.append(0)
    for i in range(df['timestampMs'].size - 1):
        delay.append(int(int(df['timestampMs'][i]) - int(df['timestampMs'][i + 1])) / 1000)
    df['delay'] = delay

    return df

def getDate(startDate, endDate, df) :
    a = df[df['date'] == endDate].index.tolist()[0]
    b = df[df['date'] == startDate].index.tolist()[0]
    return df.loc[a:(b - 1),]


def getData(nameFile, bComputeDistance, bComputeVelocity,bComputeAcceleration):
    dataFrame = importData(nameFile)
    if bComputeDistance or bComputeVelocity or bComputeAcceleration:
        dataFrame = distance.getDistance(dataFrame)
    if bComputeVelocity:
        dataFrame = distance.getVelocity(dataFrame)
    if bComputeAcceleration:
        dataFrame = distance.getAcceleration(dataFrame)
    return dataFrame