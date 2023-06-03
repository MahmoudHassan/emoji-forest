import dash
from dash import dcc, html
from dash.dependencies import Input, Output 
import plotly.graph_objects as go
import statistics
import numpy as np

app = dash.Dash(__name__)
app.css.append_css({'external_url': 'styles.css'})

# Define custom CSS styles for the input boxes
input_box_style = {
    'width': '80px',
    'height': '30px',
    'border': '2px solid #FFD700',
    'borderRadius': '5px',
    'textAlign': 'center',
    'marginRight': '10px',
    'fontSize': '16px',
    'fontWeight': 'bold',
    'color': '#FFD700',
    'backgroundColor': '#000000',
}

app.layout = html.Div(
    style={'padding': '20px'}
)

header_style = {
    'fontSize': '32px',
    'fontWeight': 'bold',
    'marginBottom': '20px'
}

story_style = {
    'backgroundColor': '#F2F2F2',
    'borderRadius': '5px',
    'padding': '20px',
    'marginBottom': '20px',
    'textAlign': 'center'
}

apples_div_style = {
    'display': 'flex',
    'alignItems': 'center',
    'marginBottom': '20px'
}

person_emoji_style = {
    'fontSize': '20px',
    'verticalAlign': 'middle',
    'marginRight': '10px'
}

friend_box_style = {
    'display': 'flex',
    'alignItems': 'center',
    'marginRight': '20px'
}

graph_style = {
    'marginBottom': '20px',
    'padding': '5px'
}

mode_div_style = {
    'backgroundColor': '#F2F2F2',
    'borderRadius': '5px',
    'padding': '20px',
    'textAlign': 'center',
    'fontWeight': 'bold',
}
dynamic_text_style = {
    'fontWeight': 'bold',
    'color': '#FF0000',
}
app.title = "Mean, Median, and Mode of Apples"
app.layout = html.Div([
    html.H1('Mean, Median, and Mode of Apples', style=header_style),

    html.Div([
        html.Div(id='mean-explanation', style=story_style),

        html.Div([
            html.Div([
                html.Div('You:', style={'marginRight': '10px', 'fontSize': '20px', 'fontWeight': 'bold'}),
                dcc.Input(id='you-input', type='number', value=10, min=0, style=input_box_style),
            ], style={'display': 'flex', 'alignItems': 'center'}),

            *[html.Div([
                html.Span("👤", style=person_emoji_style),
                html.Div(f"Friend {i+1}:", style={'fontSize': '20px', 'fontWeight': 'bold'}),
                dcc.Input(id=f'friend{i+1}-input', type='number', value=5, min=0, style=input_box_style)
            ], style=friend_box_style) for i in range(6)]
        ], style=apples_div_style),

        html.Div(dcc.Graph(id='bar-chart'), style=graph_style),
    ])

])
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('you-input', 'value')] + [Input(f'friend{i+1}-input', 'value') for i in range(6)]
)
def update_graph(you, *friends):
    # Check if any input is None
    if None in (you, *friends):
        return dash.no_update

    names = ["You"] + [f"Friend {i+1}" for i in range(6)]
    apples = [you] + list(friends)

    mean_apples = sum(apples) / len(apples)
    mode_apples = statistics.multimode(apples)
    median_apples = statistics.median(apples)

    fig = go.Figure(data=[
        go.Scatter(x=names, y=[mean_apples]*len(names), mode='lines', name='Mean Apples', fill='tozeroy', fillcolor='rgba(255, 255, 0, 0.6)'),
        go.Scatter(x=names, y=[median_apples]*len(names), mode='lines', name='Median Apples', line=dict(color='green', width=2))
    ])

    for i, name in enumerate(names):
        for j in range(int(apples[i])):
            fig.add_annotation(
                x=name,
                y=j+1,
                text="🍎",
                showarrow=False,
                font=dict(
                    size=15,
                    color="Black"
                ),
            )

    x_range = np.arange(len(names))

    if len(set(apples)) == len(apples):
        mode_text = "N/A"
    else:
        mode_text = ", ".join(str(mode) for mode in mode_apples)

        # Find all indices of mode points
        mode_indices = [i for i, apple in enumerate(apples) if apple in mode_apples]

        # Display finger pointing emoji and text for all mode points
        for idx in mode_indices:
            fig.add_annotation(
                x=names[idx],
                y=apples[idx],
                xref="x",
                yref="y",
                text="👇",
                opacity=0.8,
                showarrow=True,
                arrowhead=2,
                arrowcolor="black",
                arrowsize=1,
                arrowwidth=1,
            )
            fig.add_annotation(
                x=names[idx],
                y=apples[idx],
                xref="x",
                yref="y",
                text=f"The mode: {apples[idx]}",
                showarrow=False,
                font=dict(
                    size=12,
                    color="blue"
                ),
                yshift=20
            )

    fig.update_layout(title='Number of Apples per Person', xaxis_title='Names', yaxis_title='Number of Apples',
                      yaxis=dict(range=[0, max(apples)+1]))

    return fig
@app.callback(
    Output('mean-explanation', 'children'),
    [Input('you-input', 'value')] + [Input(f'friend{i+1}-input', 'value') for i in range(6)]
)
def update_mean_explanation(you, *friends):
    # Check if any input is None
    if None in (you, *friends):
        return dash.no_update
    
    total_people = 1 + len(friends)
    total_apples = you + sum(friends)  
    mean_apples = (total_apples + you) / total_people
    mode_apples = statistics.multimode([you] + list(friends))
    median_apples = statistics.median([you] + list(friends))

    explanation = html.Div([
        html.H4("Apple Story 🍎:"),
        html.P([
            "Imagine that we all share our apples together and divide them fairly. In that case, each one of us would have approximately ",
            html.Span("{:.2f} apples".format(mean_apples), className='dynamic-text'),
            " on average! That's the power of sharing and fairness, and that's what we call the mean or average! 🥳"
        ]),
    ])

    if len(set([you] + list(friends))) == total_people:
        explanation.children.append(html.P("There is no mode for the given apple quantities."))
    else:
        explanation.children.append(html.P([
            "The mode value represents the number of apples that appear most often. In this case, the mode is ",
            html.Span(", ".join(str(mode) for mode in mode_apples), className='dynamic-text'), "🍎"
        ]))

    explanation.children.extend([
        html.P([
            "The median value represents the middle value when the apple quantities are arranged in ascending order. It's important to note that when the total number of apple quantities is even, the median is calculated by taking the average of the two middle values. On the other hand, when the total number of apple quantities is odd, the median is the middle value directly. 🍎"
        ]),
        html.P(["The median value for the current data is: ", html.Span(str(median_apples), className='dynamic-text')]),
        html.P(["The total number of apples is: ", html.Span(str(total_apples), className='dynamic-text')]),
        html.P(["There are ", html.Span(str(total_people), className='dynamic-text'), " people in total."])
    ])

    return explanation


if __name__ == '__main__':
    app.run_server(debug=True, port=7003)
