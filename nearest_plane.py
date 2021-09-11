import pandas as pd
import requests as reqs
from scipy.spatial.distance import cdist
import schedule
import time
import sys


def closest_airplane():
    retries = 1
    success = False
    while not success:
        try:
            live_res = reqs.get('https://opensky-network.org/api/states/all?lamin=36.1934&lomin=-84.1123&lamax=39.5656&lomax=-75.1997')
            live_data = live_res.json()
            success = True
        except Exception as e:
            wait = retries * 10
            print ('Error! Waiting '+str(wait)+' secs and re-trying...' )
            sys.stdout.flush()
            time.sleep(wait)
            retries += 1


    live_df = pd.DataFrame(live_data['states'])
    live_df.columns = ['icao24','callsign','origin_country','time_position','last_contact','Lon','Lat','baro_altitude','on_ground','velocity','true_track','vertical_rate','sensors','geo_altitude','squawk','special_pupose','position_source']
    live_df['baro_altitude']= live_df['baro_altitude']*3.28084
    live_df['baro_altitude'] = live_df['baro_altitude'].fillna(0).astype('int64')
    live_df['last_contact_begin'] = live_df['last_contact'] -6400


    data2 = {'Lat': pd.Series([]),
            'Lon': pd.Series([])}##input your lat/lon you can find this by right clicking your location on google maps/earth.


    def closest_point(point, points):
        """ Find closest point from a list of points. """
        return points[cdist([point], points).argmin()]

    def match_value(df, col1, x, col2):
        """ Match value x from col1 row to value in col2. """
        return df[df[col1] == x][col2].values[0]

    df1 = live_df
    df2 = pd.DataFrame(data2)

    df1['point'] = [(x, y) for x,y in zip(df1['Lat'], df1['Lon'])]
    df2['point'] = [(x, y) for x,y in zip(df2['Lat'], df2['Lon'])]
    df1['closest']  = df1['point'] 
    df2['closest'] = [closest_point(x, list(df1['point'])) for x in df2['point']]
    df3 = df1.merge(df2, on=['closest'], how='inner')

    print('Flight:   '+df3['callsign'].to_string(index=False))
    print('Altitude: '+df3['baro_altitude'].to_string(index=False)+'ft')

schedule.every(11).seconds.do(closest_airplane)

while True:
    schedule.run_pending()
    time.sleep(1)
       
