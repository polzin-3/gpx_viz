import pandas as pd
import folium
from folium.plugins import HeatMap, HeatMapWithTime
import gpxpy
import geopandas as gpd
import numpy as np
from folium import IFrame
import base64

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
        print(filename)
        #print(len(gpx.tracks))
        if (len(gpx.tracks) != 1) | (len(gpx.tracks[0].segments) != 1):
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
            #df['time'] = df['time'].dt.floor('1min')
            #df = df.groupby('time').agg({'lon':'mean', 'lat':'mean', 'alt':'mean'}).reset_index()
            df = interp_metres(df)
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
            if df['time'].isna().sum() < 1: 
                df['time'] = df['time'].dt.floor('1min')
                df = df.groupby('time').agg({'lon':'mean', 'lat':'mean', 'alt':'mean'}).reset_index()
            df = interp_metres(df)
            print(df.shape[0])
            print("Mean lat: {}, Mean lon: {}".format(df['lat'].mean(), df['lon'].mean()))
            df_all.append(df)

    df_all = pd.concat(df_all)
    return df_all

def make_heatmap(dataframe, centre=(54.083797, -2.858426), save_as=None,
                radius=10, blur=15, min_opacity=0.4, markers=True):
    """Make folium heatmap from lat, lon data.
    
    Parameters
    ----------
    dataframe : pandas.DataFrame
        requires columns "lat", "lon" as a minimum
    centre : tuple, optional
        latitude, longitude tuple of map centrepoint
    save_as : str, optional
        filename to save html map file, if desired
    radius : int, optional
        Folium Heatmap parameter
    blur : int, optional
        Folium Heatmap parameter
    min_opacity : int, optional
        Folium Heatmap parameter
        
    Returns
    -------
    folium map object
    
    """
    m = folium.Map(location=centre, zoom_start=6)#, width='40%', height='80%')

    heat_data = dataframe[['lat', 'lon']].dropna().drop_duplicates()
    heat_data = [[row['lat'],row['lon']] for index, row in heat_data.iterrows()]
    # Plot it on the map
    HeatMap(heat_data, radius=radius, blur=blur, min_opacity=min_opacity).add_to(m)
    if markers:
        m = add_img_markers(m)
    if save_as is not None:
        m.save(save_as)
    return m

def interp_metres(data, metres=10):
    data = gpd.GeoDataFrame(data,
                            geometry=gpd.points_from_xy(data.lon, data.lat),
                            crs='epsg:4326')
    data = data.to_crs('epsg:27700')
    data['dist_diff'] = 0
    for i in data.index[:-1]:
        data.loc[i+1, 'dist_diff'] = data.loc[i, 'geometry'].distance(data.loc[i+1, 'geometry'])
    data['dist'] = data['dist_diff'].cumsum()
    new_dist = np.arange(0, data['dist'].max(), metres)  # 10 metre sampling
    lat = np.interp(new_dist, data['dist'].values, data['lat'].values)
    lon = np.interp(new_dist, data['dist'].values, data['lon'].values)
    #alt = np.interp(new_dist, data['dist'].values, data['alt'].values)
    new_data = pd.DataFrame({'lon':lon, 'lat':lat})
    new_data['alt'] = np.nan
    new_data['time'] = np.nan
    return new_data

def add_img_markers(m):
    images = ['Darren','Dovestones','Ewan','Harry','John','Jon','Laura','Stephen']
    latlon = [(51.5525,-0.8051),(53.5312,-1.9740),(53.5056,-2.2919),
            (54.4569,-2.9498),(57.2236,-2.3219),(53.5312,-1.9740),
            (53.2756,-2.7396),(53.4262,-2.3313)]
    # Add markers
    for name,coord in zip(images, latlon):
        tmp_b64 = base64.b64encode(open(name + '.png', 'rb').read())
        html_img = '<img src="data:image/png;base64,{}" style="height:180px;">'.format
        iframe = IFrame(html_img(tmp_b64.decode('ascii')), width=200, height=200)
        popup = folium.Popup(iframe)
        folium.Marker([coord[0], coord[1]],
                    popup=popup, tooltip='Click me!').add_to(m)
    return m