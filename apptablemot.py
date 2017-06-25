import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import pandas as pd

intervals ={0:'Baseline',1:'1 mth'}
df = pd.read_csv('data/admin.csv')


#Calculate diffs
def diffdata(df):
    baselinedf = df[df.interval == 0]
    onemonthdf = df[df.interval == 1]
    diffdf = pd.DataFrame(baselinedf.Subject.unique(), columns=['Subject'])
    fields = {'MOTML': [], 'MOTSDL':[]}
    age = []
    gender = []
    # NB change to dynamic intervals -> df[(df.interval==0) & (df.Subject == i)]
    for i in baselinedf.Subject.unique():
        age.append(baselinedf[baselinedf['Subject'] == i]['Age'].get_values()[0])
        gender.append(baselinedf[baselinedf['Subject'] == i]['Gender'].get_values()[0])
        if (i in onemonthdf['Subject'].values):
            for field in fields:
                d0 = baselinedf[baselinedf['Subject'] == i][field]
                d1 = onemonthdf[onemonthdf['Subject'] == i][field]
                d = d1.get_values()[0]-d0.get_values()[0]
                fields[field].append(d)
        else:
            for field in fields:
                fields[field].append(None)

    diffdf = diffdf.assign(Age = age, Gender = gender, dMOTML=fields['MOTML'], dMOTSDL = fields['MOTSDL'])

    return diffdf

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.loc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

app = dash.Dash()
diff = diffdata(df)

app.layout = html.Div(children=[
    html.H4(children='CANTAB  MOT DATA'),
    dcc.Graph(
        id='mot-vs-age',
        figure={
            'data': [
                go.Scatter(
                    x=df[df['interval'] == i]['Age'],
                    y=df[df['interval'] == i]['MOTML'],
                    text=df[df['interval'] == i]['Subject'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=intervals[i]
                ) for i in df.interval.unique()
            ],
            'layout': go.Layout(
                xaxis={'type': 'log', 'title': 'Age'},
                yaxis={'title': 'MOTML'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    ),
    html.H4(children='MOTML: Month 1 - baseline'),
    dcc.Graph(
        id='dmot-vs-age',
        figure={
            'data': [
                go.Scatter(
                    x=diff[diff['Gender'] == i]['Age'],
                    y=diff[diff['Gender'] == i]['dMOTML'],
                    text=diff[diff['Gender'] == i]['Subject'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in diff.Gender.unique()
            ],
            'layout': go.Layout(
                xaxis={'type': 'log', 'title': 'Age'},
                yaxis={'title': 'dMOTML'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    ),
    generate_table(df)
])


app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

if __name__ == '__main__':
    app.run_server(debug=True, port=8088)