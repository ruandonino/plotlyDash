import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_dashboard():
    # ==============================================================================
    # 1. DATA PREPARATION
    # ==============================================================================

    # --- Data for Treemap ---
    try:
        df_products = pd.read_csv('../data/products.csv')
    except FileNotFoundError:
        print("Product CSV not found. Using dummy product data.")
        product_data = {
            'category': ['Electronics', 'Electronics', 'Furniture', 'Furniture', 'Home Appliances', 'Home Appliances', 'Sports', 'Clothing'],
            'sub_category': ['Laptops', 'Smartphones', 'Chairs', 'Tables', 'Refrigerators', 'Microwaves', 'Bicycles', 'Shirts'],
            'value': [1500, 1200, 300, 500, 800, 200, 600, 150]
        }
        df_products = pd.DataFrame(product_data)

    # --- Data for Geographical Map ---
    geo_data = {
        'state_code': ['SP', 'RJ', 'MG', 'BA', 'PR', 'RS', 'PE', 'CE', 'PA', 'SC', 'GO', 'MA', 'AM', 'ES'],
        'sales': [12000, 8500, 7000, 5500, 6000, 4800, 4200, 3800, 3000, 4500, 3200, 2500, 2000, 2800]
    }
    df_geo = pd.DataFrame(geo_data)

    # Color map for the treemap categories
    color_map = {
         'Home Appliances': '#d8d8d8',
         'Electronics': '#5a6d8b',
         'Sports': '#66bfc7',
         'Furniture': '#a14df2',
         'Clothing': '#3333a6'
     }

    # ==============================================================================
    # 2. CREATE INDIVIDUAL FIGURES
    # ==============================================================================

    # --- Create Geographical Map Figure (Left side) ---
    fig_geo = px.choropleth(
        df_geo,
        geojson="https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
        locations='state_code',
        featureidkey="properties.sigla",
        color='sales',
        color_continuous_scale="Viridis",
        scope="south america"
    )

    # --- Create Treemap Figure (Right side) ---
    fig_treemap = px.treemap(
        df_products,
        path=['category', 'sub_category'],
        values='value',
        color='category',
        color_discrete_map=color_map
    )
    # Add invisible traces for the legend
    for category_name, color in color_map.items():
        fig_treemap.add_trace(go.Scatter(
            x=[None], y=[None], mode='markers',
            marker=dict(size=15, color=color, symbol='square'),
            name=category_name, showlegend=True
        ))

    # ==============================================================================
    # 3. COMBINE FIGURES INTO A SINGLE DASHBOARD
    # ==============================================================================

    # Create a figure with subplots (subplot_titles removed)
    fig_combined = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'choropleth'}, {'type': 'treemap'}]]
    )

    # Add geo traces
    for trace in fig_geo.data:
        fig_combined.add_trace(trace, row=1, col=1)

    # Add treemap and legend traces
    for trace in fig_treemap.data:
        if trace.type == 'treemap':
            fig_combined.add_trace(trace, row=1, col=2)
        elif trace.type == 'scatter':
            fig_combined.add_trace(trace)


    # ==============================================================================
    # 4. UPDATE LAYOUT AND STYLING
    # ==============================================================================

    # --- Update Treemap-specific text and hover info ---
    treemap_trace_index = -1
    for i, trace in enumerate(fig_combined.data):
        if trace.type == 'treemap':
            treemap_trace_index = i
            break

    if treemap_trace_index != -1:
        fig_combined.data[treemap_trace_index].textinfo = 'label+value+percent parent'
        fig_combined.data[treemap_trace_index].texttemplate = "<b>%{label}</b><br>%{value}<br>%{percentParent:.1%}"
        fig_combined.data[treemap_trace_index].hovertemplate = '<b>%{label}</b><br>Value:%{value}<br>Share of Parent: %{percentParent:.1%}<extra></extra>'
        fig_combined.data[treemap_trace_index].marker.pad = dict(t=2, l=2, r=2, b=2)


    # --- Update overall layout ---
    fig_combined.update_layout(
        # Manually create annotations to act as subplot titles
        annotations=[
            dict(
                text="Sales Distribution in Brazil",
                x=0.22, y=1.0, # Position for the left title
                xref='paper', yref='paper',
                font=dict(size=16), showarrow=False, yanchor='bottom'
            ),
            dict(
                text="Product Distribution",
                x=0.61, y=1.05, # Position for the right title
                xref='paper', yref='paper',
                font=dict(size=16), showarrow=False, yanchor='bottom'
            )
        ],
        legend=dict(
            orientation="h",
            # Anchor from the top to place it below the Y coordinate
            yanchor="top",
            # This y value now places it just below the custom annotation
            y=1.05,
            xanchor="center",
            x=0.73
        ),
        coloraxis_showscale=False,
        margin=dict(t=100, l=25, r=25, b=25),
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Rockwell"
        ),
        xaxis_visible=False,
        yaxis_visible=False
    )
    fig_combined.update_geos(fitbounds="locations", row=1, col=1)

    fig_combined.show()


if __name__ == "__main__":
    create_dashboard()