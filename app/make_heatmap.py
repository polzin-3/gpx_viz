import glob
import functions

files = glob.glob('../GPX/*gpx')
df = functions.read_data(files)
df.to_pickle('Coordinates_data.pkl')
#functions.make_heatmap(df, radius=10, blur=15, min_opacity=0.4,
#                        save_as='heatmap.html')