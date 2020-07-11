import glob
import functions

files = glob.glob('GPX/*gpx')
df = functions.read_data(files)
functions.make_heatmap(df, save_as='heatmap.html')