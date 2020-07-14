import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import base64
import functions as appfun

app = dash.Dash()

print("Reading data...")
data = pd.read_pickle('Coordinates_data.pkl')
# images
peak_b64 = base64.b64encode(open('peaklogo.png', 'rb').read()).decode('ascii')
fare_b64 = base64.b64encode(open('fareshare_logo.jpg', 'rb').read()).decode('ascii')
print("Done.")

colors = {
    'background': 'white',
    'text': '#000033',
    'pink_text': '#ff3399'
}
fonts  = {
    'peak1': 'Montserrat',
    'peak2': 'Open Sans'
}
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Div(
        html.Img(src='data:image/png;base64,{}'.format(peak_b64),
        style={'height':'100px'}
        ),
    style={'display': 'inline-block'}
    ),

    html.Div(
        html.Img(src='data:image/png;base64,{}'.format(fare_b64),
        style={'height':'100px'}
        ),
    style={'display': 'inline-block'}
    ),

    html.Div(
        #children='United, we hike',
        children=html.P(["United, ", html.Span("we hike",
                                                style={'font-weight':'bold'})]),
        style={
            'textAlign': 'left',
            'color': colors['text'],
            'fontFamily': fonts['peak1'],
            'paddingLeft': '10px'
        },
    ),

    html.Div(
        [dcc.Slider(
            id='hm_radius',
            min=1,
            max=30,
            step=1,
            marks={
                1: '1',
                10: '10',
                20: '20',
                30: '30'
            },
            value=10,
            tooltip={'always_visible':False}
        ),
        html.Span("Radius", id='r_slide_txt'),
        dbc.Tooltip("Radius of each point of the heatmap",
                    target='r_slide_txt', placement='bottom',
                    style={'fontFamily': fonts['peak1'], 'color': colors['pink_text']})
        ],
        style={'width': '15%', 'display': 'inline-block', 'padding': '10px',
        'fontFamily': fonts['peak1'], 'color': colors['text'], 'fontSize': '12px',
        'textAlign': 'center'}
    ),

    html.Div(
        [dcc.Slider(
            id='hm_blur',
            min=1,
            max=20,
            step=1,
            marks={
                1: '1',
                10: '10',
                20: '20'
            },
            value=15,
            tooltip={'always_visible':False}
        ),
        html.Span("Blur", id='b_slide_txt'),
        dbc.Tooltip("Amount of blur",
                    target='b_slide_txt', placement='bottom',
                    style={'fontFamily': fonts['peak1'], 'color': colors['pink_text']})
        ],
        style={'width': '15%', 'display': 'inline-block', 'padding': '10px',
        'fontFamily': fonts['peak1'], 'color': colors['text'], 'fontSize': '12px',
        'textAlign': 'center'}
    ),

    html.Div(
        [dcc.Slider(
            id='hm_min_opacity',
            min=0.1,
            max=1.0,
            step=0.1,
            marks={
                0.1: '0.1',
                0.5: '0.5',
                1: '1'
            },
            value=0.4,
            tooltip={'always_visible':False}
        ),
        html.Span("Min Opacity", id='op_slide_txt'),
        dbc.Tooltip("The minimum opacity the heat will start at",
                    target='op_slide_txt', placement='bottom',
                    style={'fontFamily': fonts['peak1'], 'color': colors['pink_text']})
        ],
        style={'width': '15%', 'display': 'inline-block', 'padding': '10px',
        'fontFamily': fonts['peak1'], 'color': colors['text'], 'fontSize': '12px',
        'textAlign': 'center'}
    ),

    html.Div(
        html.Button(id='default', n_clicks=0, children='Reset',
                    style={'fontFamily': fonts['peak1'], 'fontSize': '16px',
                           'fontWeight': 'bold', 'color': colors['text'],
                           'background': colors['pink_text']}),
    style={'width': '10%', 'display': 'inline-block', 'textAlign':'center',
            'padding': '10px'}
    ),

    html.Div(id="map_div",
            style={'width': '50%', 'textAlign':'center', 'height': '500px',
                'color': colors['text'], 'fontFamily': fonts['peak1'],
                'padding': '10px'}
    )
])

@app.callback(
    Output('map_div', 'children'),
    [Input('hm_radius', 'value'),
     Input('hm_blur', 'value'),
     Input('hm_min_opacity', 'value')])
def get_map(radius, blur, min_opacity):
    appfun.make_heatmap(data, centre=(54.083797, -2.858426), save_as='heatmap.html',
                        radius=radius, blur=blur, min_opacity=min_opacity)
    return html.Iframe(id="map",srcDoc=open('heatmap.html', 'r').read(),
                        width='100%', height=500)

@app.callback(
    [Output('hm_radius', 'value'),
    Output('hm_blur', 'value'),
    Output('hm_min_opacity', 'value')],
    [Input('default', 'n_clicks')])
def get_map(n_clicks):
    return [10, 15, 0.4]


if __name__ == '__main__':
    app.run_server(debug=True)