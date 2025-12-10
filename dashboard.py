import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# ------------------------------
# Load and Prepare Data
# ------------------------------
df = pd.read_csv('Sleep_health_and_lifestyle_dataset.csv')
df.columns = df.columns.str.strip()
df['Sample ID'] = range(1, len(df) + 1)

# ------------------------------
# Initialize Dash App with Bootstrap Theme
# ------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = "Sleep & Lifestyle Analytics Dashboard"

# ------------------------------
# Styling Constants
# ------------------------------
COLORS = {
    'primary': '#2C3E50',
    'secondary': '#3498DB',
    'accent': '#E74C3C',
    'background': '#F8F9FA',
    'card': '#FFFFFF',
    'text': '#2C3E50'
}

# ------------------------------
# Layout Components
# ------------------------------
header = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Sleep & Lifestyle Analytics Dashboard", 
                   className="display-4 fw-bold mb-2",
                   style={'color': COLORS['primary']}),
            html.P("Interactive exploration of sleep patterns, stress levels, and physical activity",
                  className="lead text-muted mb-4")
        ])
    ])
], fluid=True, className="py-4")

# Filter Controls
filters = dbc.Card([
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.Label("Sleep Duration Range (hours)", className="fw-semibold mb-2"),
                dcc.RangeSlider(
                    id='sleep-filter',
                    min=df['Sleep Duration'].min(),
                    max=df['Sleep Duration'].max(),
                    value=[df['Sleep Duration'].min(), df['Sleep Duration'].max()],
                    step=0.5,
                    marks={i: {'label': f'{i}h', 'style': {'fontSize': '11px'}} 
                           for i in range(int(df['Sleep Duration'].min()), 
                                        int(df['Sleep Duration'].max()) + 1, 1)},
                    tooltip={"placement": "bottom", "always_visible": False}
                )
            ], md=12, className="mb-4")
        ]),
        dbc.Row([
            dbc.Col([
                html.Label("Stress Level", className="fw-semibold mb-2"),
                dcc.Dropdown(
                    id='stress-filter',
                    options=[{'label': f'Level {s}', 'value': s} 
                            for s in sorted(df['Stress Level'].unique())],
                    multi=True,
                    placeholder="All stress levels",
                    className="mb-2"
                )
            ], md=6),
            dbc.Col([
                html.Label("Physical Activity Level", className="fw-semibold mb-2"),
                dcc.Dropdown(
                    id='activity-filter',
                    options=[{'label': a, 'value': a} 
                            for a in sorted(df['Physical Activity Level'].unique())],
                    multi=True,
                    placeholder="All activity levels",
                    className="mb-2"
                )
            ], md=6)
        ])
    ])
], className="shadow-sm mb-4")

# Summary Statistics Cards
stats_cards = dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H6("Total Samples", className="text-muted mb-2"),
                html.H3(id="stat-total", className="mb-0 fw-bold", 
                       style={'color': COLORS['secondary']})
            ])
        ], className="shadow-sm h-100")
    ], md=3),
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H6("Avg Sleep Duration", className="text-muted mb-2"),
                html.H3(id="stat-sleep", className="mb-0 fw-bold",
                       style={'color': COLORS['secondary']})
            ])
        ], className="shadow-sm h-100")
    ], md=3),
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H6("Avg Sleep Quality", className="text-muted mb-2"),
                html.H3(id="stat-quality", className="mb-0 fw-bold",
                       style={'color': COLORS['secondary']})
            ])
        ], className="shadow-sm h-100")
    ], md=3),
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H6("Avg Stress Level", className="text-muted mb-2"),
                html.H3(id="stat-stress", className="mb-0 fw-bold",
                       style={'color': COLORS['secondary']})
            ])
        ], className="shadow-sm h-100")
    ], md=3)
], className="mb-4")

# Visualization Grid
plots = dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                dcc.Graph(id='plot-overview', config={'displayModeBar': True})
            ])
        ], className="shadow-sm h-100")
    ], md=6, className="mb-4"),
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                dcc.Graph(id='plot-stress', config={'displayModeBar': True})
            ])
        ], className="shadow-sm h-100")
    ], md=6, className="mb-4"),
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                dcc.Graph(id='plot-activity', config={'displayModeBar': True})
            ])
        ], className="shadow-sm h-100")
    ], md=6, className="mb-4"),
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                dcc.Graph(id='plot-comprehensive', config={'displayModeBar': True})
            ])
        ], className="shadow-sm h-100")
    ], md=6, className="mb-4")
])

# ------------------------------
# Main Layout
# ------------------------------
app.layout = dbc.Container([
    header,
    filters,
    stats_cards,
    plots
], fluid=True, style={'backgroundColor': COLORS['background'], 'minHeight': '100vh'})

# ------------------------------
# Helper Functions
# ------------------------------
def filter_dataframe(df, sleep_range=None, stress=None, activity=None):
    """Apply filters to dataframe"""
    filtered = df.copy()
    
    if sleep_range:
        filtered = filtered[
            (filtered['Sleep Duration'] >= sleep_range[0]) &
            (filtered['Sleep Duration'] <= sleep_range[1])
        ]
    
    if stress and len(stress) > 0:
        filtered = filtered[filtered['Stress Level'].isin(stress)]
    
    if activity and len(activity) > 0:
        filtered = filtered[filtered['Physical Activity Level'].isin(activity)]
    
    return filtered

def create_base_layout():
    """Common layout settings for all plots"""
    return {
        'template': 'plotly_white',
        'font': {'family': 'Inter, sans-serif', 'size': 12},
        'margin': {'l': 50, 'r': 30, 't': 50, 'b': 50},
        'hovermode': 'closest'
    }

# ------------------------------
# Callbacks
# ------------------------------
@app.callback(
    [
        Output('stat-total', 'children'),
        Output('stat-sleep', 'children'),
        Output('stat-quality', 'children'),
        Output('stat-stress', 'children'),
        Output('plot-overview', 'figure'),
        Output('plot-stress', 'figure'),
        Output('plot-activity', 'figure'),
        Output('plot-comprehensive', 'figure'),
    ],
    [
        Input('sleep-filter', 'value'),
        Input('stress-filter', 'value'),
        Input('activity-filter', 'value'),
    ]
)
def update_dashboard(sleep_range, selected_stress, selected_activity):
    """Update all dashboard components based on filters"""
    
    # Apply filters
    filtered = filter_dataframe(
        df, 
        sleep_range=sleep_range,
        stress=selected_stress,
        activity=selected_activity
    )
    
    # Calculate statistics
    total_samples = len(filtered)
    avg_sleep = f"{filtered['Sleep Duration'].mean():.1f}h"
    avg_quality = f"{filtered['Quality of Sleep'].mean():.1f}/10"
    avg_stress = f"{filtered['Stress Level'].mean():.1f}/10"
    
    # Plot 1: Sleep Duration Distribution
    fig1 = px.histogram(
        filtered, 
        x='Sleep Duration',
        nbins=25,
        title='Sleep Duration Distribution',
        labels={'Sleep Duration': 'Sleep Duration (hours)', 'count': 'Number of Individuals'},
        color_discrete_sequence=[COLORS['secondary']]
    )
    fig1.update_traces(hovertemplate='Duration: %{x}h<br>Count: %{y}<extra></extra>')
    fig1.update_layout(**create_base_layout(), bargap=0.1)
    
    # Plot 2: Sleep Quality vs Duration by Stress Level
    fig2 = px.scatter(
        filtered,
        x='Sleep Duration',
        y='Quality of Sleep',
        color='Stress Level',
        size='Stress Level',
        title='Sleep Quality vs Duration by Stress Level',
        labels={
            'Sleep Duration': 'Sleep Duration (hours)',
            'Quality of Sleep': 'Sleep Quality (0-10)',
            'Stress Level': 'Stress Level'
        },
        color_continuous_scale='RdYlGn_r',
        hover_data=['Physical Activity Level']
    )
    fig2.update_traces(hovertemplate='<b>Sleep Duration:</b> %{x}h<br>' +
                                    '<b>Sleep Quality:</b> %{y}<br>' +
                                    '<b>Stress Level:</b> %{marker.color}<extra></extra>')
    fig2.update_layout(**create_base_layout())
    
    # Plot 3: Sleep Duration by Physical Activity Level
    fig3 = px.box(
        filtered,
        x='Physical Activity Level',
        y='Sleep Duration',
        color='Physical Activity Level',
        title='Sleep Duration by Physical Activity Level',
        labels={
            'Physical Activity Level': 'Activity Level',
            'Sleep Duration': 'Sleep Duration (hours)'
        },
        points='all',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig3.update_traces(hovertemplate='<b>Activity:</b> %{x}<br>' +
                                    '<b>Sleep Duration:</b> %{y}h<extra></extra>')
    fig3.update_layout(**create_base_layout())
    
    # Plot 4: Comprehensive Density Heatmap
    fig4 = px.density_heatmap(
        filtered,
        x='Sleep Duration',
        y='Quality of Sleep',
        marginal_x='histogram',
        marginal_y='histogram',
        title='Sleep Duration vs Quality Density Map',
        labels={
            'Sleep Duration': 'Sleep Duration (hours)',
            'Quality of Sleep': 'Sleep Quality (0-10)'
        },
        color_continuous_scale='Viridis'
    )
    fig4.update_layout(**create_base_layout())
    
    return (total_samples, avg_sleep, avg_quality, avg_stress, 
            fig1, fig2, fig3, fig4)

# ------------------------------
# Run Server
# ------------------------------
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
