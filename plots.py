import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def summary_plot():
    """ Makes the plots that we need to see """
    df = pd.read_csv('export_run.csv')
    df.head()
    fig = make_subplots(rows=2, cols=2, subplot_titles=('Unemployment', 'GDP', 'Indexed price level', 'Phillips curve'))

    fig.add_trace(go.Scatter(x=df['t'], y=df['unemployment_rate']), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['t'], y=df['gdp']), row=1, col=2)
    fig.add_trace(go.Scatter(x=df['t'], y=df['indexed_price_level']), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['average_needs_ratio'][1:], y=df['inflation'][1:], mode='markers'), row=2, col=2)
    fig.update_layout(height=2500, width=3500, title_text="Economic Analysis")

    fig.show()


def plot_on_command():
    """ Makes the plots that you want to see """
    df = pd.read_csv('export_run.csv')

    x = 'no'

    while x != 'yes':
        series = input("What do you want to see?").lower()
        end = {"nothing", "none", "stop", "no"}

        if series in end:
            break
        elif series not in df.columns:
            print("Sorry, I don't have that. Please try something else.")
            continue
        else:
            fig = px.line(df, x='t', y=series, title=f'{series} over time')
            fig.show()
            x = input("Is that all?").lower()
