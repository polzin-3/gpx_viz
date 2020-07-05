import pandas as pd
import folium
from folium.plugins import HeatMap, HeatMapWithTime
import gpxpy

def read_data(filepaths):
    """Reads multiple gpx files into a single pandas DataFrame.
    
    Parameters
    ----------
    filepaths : list of str
        paths to gpx files
        
    Returns
    -------
    pandas.DataFrame
        timestamp and location data.
    
    """
    df_all = []
    for filename in filepaths:
        gpx_file = open(filename, 'r')
        gpx = gpxpy.parse(gpx_file)
        # check that data is all in .points attribute of first segment and first track
        if (len(gpx.tracks) != 1) | (len(gpx.tracks[0].segments) != 1):
            #print(filename)
            #print(len(gpx.tracks))
            df = pd.DataFrame(columns=['lon', 'lat', 'alt', 'time'])
            for i in range(len(gpx.tracks)):
                #print(len(gpx.tracks[i].segments))
                for j in range(len(gpx.tracks[0].segments)):
                    #print(len(gpx.tracks[i].segments[j].points))
                    data = gpx.tracks[i].segments[j].points
                    for point in data:
                        df = df.append({'lon':point.longitude,
                                        'lat':point.latitude,
                                        'alt':point.elevation,
                                        'time':point.time},
                                       ignore_index=True)
            df['binned_time'] = df['time'].dt.floor('1min')
            df = df.groupby('binned_time').agg({'lon':'mean', 'lat':'mean', 'alt':'mean'}).reset_index()
            df_all.append(df)

        else:
            data = gpx.tracks[0].segments[0].points
            # put into dataframe
            df = pd.DataFrame(columns=['lon', 'lat', 'alt', 'time'])
            for point in data:
                df = df.append({'lon':point.longitude,
                                'lat':point.latitude,
                                'alt':point.elevation,
                                'time':point.time},
                               ignore_index=True)
            # group into 1 minute bins
            df['binned_time'] = df['time'].dt.floor('1min')
            df = df.groupby('binned_time').agg({'lon':'mean', 'lat':'mean', 'alt':'mean'}).reset_index()
            df_all.append(df)

    df_all = pd.concat(df_all)
    return df_all

def make_heatmap(dataframe, centre=(54.083797, -2.858426), save_as=None):
    """Make folium heatmap from lat, lon data.
    
    Parameters
    ----------
    dataframe : pandas.DataFrame
        requires columns "lat", "lon" as a minimum
    centre : tuple, optional
        latitude, longitude tuple of map centrepoint
    save_as : str, optional
        filename to save html map file, if desired
        
    Returns
    -------
    folium map object
    
    """
    m = folium.Map(location=centre, zoom_start=6, width='40%')#, height='80%')

    heat_data = dataframe[['lat', 'lon']].dropna().drop_duplicates()
    heat_data = [[row['lat'],row['lon']] for index, row in heat_data.iterrows()]
    # Plot it on the map
    HeatMap(heat_data, radius=10, blur=15, min_opacity=.4).add_to(m)
    if save_as is not None:
        m.save(save_as)
    return m