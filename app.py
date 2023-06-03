import dash
from dash import dcc, html, Dash, no_update
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

import dash_table

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title="🌳 Emoji Forest Statistics 🌲"
# Define initial empty DataFrame
df = pd.DataFrame(columns=['Height of Emoji Tree'])

app.layout = dbc.Container([
    html.H1("🌳 Emoji Forest Statistics 🌲"),

    dbc.Row([
        dbc.Col([
            html.H6("Grow some Emoji Trees in your forest! Select how many:"),
            dbc.Tooltip(
                "Move the slider to choose the number of trees you want to grow, "
                "then click this button to watch them spring up! 🌱",
                target="generate-button",
                placement="bottom",
            ),
            dcc.Slider(id='slider', min=10, max=20, value=20, step=1),
            html.Div(id='slider-output-container'),
            dbc.Button('Grow Emoji Trees! 🌱',
                       id='generate-button', color="success"),
        ]),
        dbc.Col([
            html.H6("Found a special tree? Enter its height here (cm):"),
            dcc.Input(id='numeric-input', type='number', min=0),
            dbc.Button('Measure Special Tree 📏🌳',
                       id='add-button', color="warning"),
            html.Div(id='numeric-output'),
        ])
    ], style={'margin-top': '20px'}),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='data-table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.head(5).to_dict('records'),
                style_cell={'textAlign': 'center'},
                page_size=5,
                style_header={
                    'backgroundColor': 'rgb(30, 30, 30)',
                    'color': 'white'
                },
            )
        ]),
    ], style={'margin-top': '20px'}),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            html.Div(id='histogram-text', style={'text-align': 'center'}),
            dcc.Graph(id='histogram'),
            dcc.Graph(id='box-plot'),
            dcc.Graph(id='scatter-plot')  # Scatter plot with points and mean line
        ]),
    ], style={'margin-top': '20px'}),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            html.Div(className="stats-widget", id='stats-summary')
        ]),
    ], style={'margin-top': '20px'}),

], fluid=True)


@app.callback(
    Output('slider-output-container', 'children'),
    Input('slider', 'value')
)
def update_slider_output(value):
    return f"You're growing {value} trees! 🌳🌳"


@app.callback(
    Output('numeric-output', 'children'),
    Input('add-button', 'n_clicks'),
    State('numeric-input', 'value')
)
def add_data(n_clicks, value):
    global df
    if n_clicks is not None and n_clicks > 0:
        # Add specific data point to data
        df = df.append({'Height of Emoji Tree': value}, ignore_index=True)
        return f'Height of special tree measured: {value} cm! 📏🌳'


@app.callback(
    Output('data-table', 'data'),
    Output('data-table', 'columns'),
    Output('histogram', 'figure'),
    Output('box-plot', 'figure'),
    Output('scatter-plot', 'figure'),
    Output('stats-summary', 'children'),
    Output('histogram-text', 'children'),
    Input('generate-button', 'n_clicks'),
    Input('slider', 'value'),
    Input('add-button', 'n_clicks'),
    State('numeric-input', 'value')
)
def update_data(n1, n_points, n2, value):
    global df
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'generate-button' and n1 > 0:
        # Generate n_points of random data
        # Heights of emoji trees
        data = np.random.normal(loc=150, scale=30, size=n_points)
        df = pd.DataFrame(data, columns=['Height of Emoji Tree'])

    if df.empty:
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update

    # Create the plots
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(x=df['Height of Emoji Tree'], nbinsx=20,
                                    marker_color='green', name='Height', marker_line=dict(color='black', width=1)))

    mean_value = df['Height of Emoji Tree'].mean()
    median_value = df['Height of Emoji Tree'].median()

    # Add mean and median as separate scatter traces
    fig_hist.add_trace(go.Scatter(x=[mean_value, mean_value], y=[0, 20], mode='lines',
                                  line=dict(color='red', width=2), name='Mean'))

    fig_hist.add_trace(go.Scatter(x=[median_value, median_value], y=[0, 20], mode='lines',
                                  line=dict(color='blue', width=2), name='Median'))

    fig_hist.update_layout(
        title_text='Histogram: Distribution of Emoji Tree Heights',
        xaxis_title='Height (cm)',
        yaxis_title='Count',
        showlegend=True
    )

    # Add shape flag based on skewness
    skewness = df['Height of Emoji Tree'].skew()
    if skewness < -1:
        shape_flag = "Left Skew"
    elif skewness > 1:
        shape_flag = "Right Skew"
    else:
        shape_flag = "Symmetrical"

    # Update histogram text annotation
    histogram_text = f"Shape: {shape_flag}"

    # Create the box plot
    fig_box = go.Figure()
    fig_box.add_trace(go.Box(
        y=df['Height of Emoji Tree'], boxpoints='outliers', marker_color='darkgreen'))

    fig_box.update_layout(
        title_text='Box Plot: Emoji Tree Heights',
        yaxis_title='Height (cm)'
    )

    # Calculate the statistics
    range_value = np.ptp(df['Height of Emoji Tree'])
    q75, q50, q25 = np.percentile(df['Height of Emoji Tree'], [75, 50, 25])
    iqr = q75 - q25
    std_dev = np.std(df['Height of Emoji Tree'])
    variance = np.var(df['Height of Emoji Tree'])

    stats_summary = [
        html.H4('📊 Emoji Tree Heights Statistics'),
        html.P(
            f"Range (difference between highest and lowest height): {range_value:.2f} cm"),
        html.P(
            f"Interquartile Range (IQR - range of the middle 50% of heights): {iqr:.2f} cm"),
        html.P(
            f"Standard Deviation (measure of height variability): {std_dev:.2f} cm"),
        html.P(
            f"Variance (square of standard deviation): {variance:.2f} cm^2"),
        html.P(f"Shape of the data: {shape_flag}")
    ]

    # Create the scatter plot
    fig_scatter = go.Figure()

    # Add scatter points
    fig_scatter.add_trace(go.Scatter(
        x=df.index,
        y=df['Height of Emoji Tree'],
        mode='markers',
        marker=dict(
            size=10,
            color='green',
            line=dict(
                color='black',
                width=1
            )
        ),
        name='Tree Heights'
    ))

    # Calculate the upper and lower bounds for the shaded area
    upper_bound = mean_value + std_dev
    lower_bound = mean_value - std_dev

    # Add shaded area for one standard deviation
    fig_scatter.add_shape(
        type='rect',
        x0=0,
        y0=lower_bound,
        x1=len(df.index) - 1,
        y1=upper_bound,
        fillcolor='lightyellow',
        opacity=0.3,
        line=dict(
            color='rgba(0,0,0,0)',
        ),
        name='One Standard Deviation'
    )

    # Add vertical dashed lines to the mean height
    for index, height in enumerate(df['Height of Emoji Tree']):
        diff = height - mean_value
        fig_scatter.add_shape(
            type="line",
            x0=index,
            y0=height,
            x1=index,
            y1=mean_value,
            line=dict(
                color="red",
                width=1,
                dash="dash",
            ),
        )
        fig_scatter.add_annotation(
            x=index,
            y=(height + mean_value) / 2,
            text=f"{diff:.2f} cm",
            showarrow=False,
            font=dict(size=10, color='black'),
            align='center',
            valign='middle'
        )

    # Add mean line
    fig_scatter.add_trace(go.Scatter(
        x=df.index,
        y=[mean_value] * len(df),
        mode='lines',
        line=dict(color='red', width=2),
        name='Mean'
    ))

    fig_scatter.update_layout(
        title_text='Scatter Plot: Emoji Tree Heights',
        xaxis_title='Tree',
        yaxis_title='Height (cm)',
        showlegend=True
    )

    # Update data table
    table_columns = [{"name": i, "id": i} for i in df.columns]
    table_data = df.to_dict('records')

    return table_data, table_columns, fig_hist, fig_box, fig_scatter, stats_summary, histogram_text


if __name__ == '__main__':
    app.run_server(debug=True, port=7003)
