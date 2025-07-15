import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path


def create_dashboard():
    # ==============================================================================
    # 1. DATA PREPARATION
    # ==============================================================================

    # --- Construct robust paths to data files ---
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir.parent / 'data'
    products_file = data_dir / 'products.csv'
    sales_file = data_dir / 'sales_summary.csv'

    # --- Data for Treemap ---
    try:
        df_products = pd.read_csv(products_file)
    except FileNotFoundError:
        print("Product CSV not found. Using dummy product data.")
        product_data = {
            'category': ['Electronics', 'Electronics', 'Furniture', 'Furniture', 'Home Appliances', 'Home Appliances',
                         'Sports', 'Clothing'],
            'sub_category': ['Laptops', 'Smartphones', 'Chairs', 'Tables', 'Refrigerators', 'Microwaves', 'Bicycles',
                             'Shirts'],
            'value': [1500, 1200, 300, 500, 800, 200, 600, 150]
        }
        df_products = pd.DataFrame(product_data)

    # --- Data for Geographical Map (USA) ---
    try:
        df_sales = pd.read_csv(sales_file)
    except FileNotFoundError:
        print("Sales summary CSV not found. Using dummy sales data.")
        sales_data = {
            'state_usa': ['California', 'Texas', 'Florida', 'New York', 'Pennsylvania',
                          'Illinois', 'Ohio', 'Georgia', 'North Carolina', 'Michigan',
                          'California', 'Texas', 'Florida', 'New York'],
            'total_sales': [125000, 180000, 150000, 140000, 90000, 110000, 85000,
                            95000, 78000, 70000, 130000, 170000, 160000, 120000]
        }
        df_sales = pd.DataFrame(sales_data)

    # Aggregate sales data by state
    df_geo = df_sales.groupby('state_usa')['total_sales'].sum().reset_index()

    # --- Data for Bar Chart (Monthly Promotional Sales Percentage) ---
    df_bar = df_sales.copy()
    # Calculate promotional sales for each record
    df_bar['promo_sales'] = df_bar['total_sales'] * df_bar['percentage_promo']
    # Group by month and sum total sales and promo sales
    monthly_summary = df_bar.groupby('month').agg(
        total_sales=('total_sales', 'sum'),
        promo_sales=('promo_sales', 'sum')
    ).reset_index()
    # Calculate the overall promotional percentage for the month
    monthly_summary['promo_percentage'] = (monthly_summary['promo_sales'] / monthly_summary['total_sales'])

    # Add state abbreviations for the scatter_geo map
    us_state_to_abbrev = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
        "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
        "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
        "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
        "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
        "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
        "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
        "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
        "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
        "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
    }
    df_geo['state_code'] = df_geo['state_usa'].map(us_state_to_abbrev)

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

    # --- Create Geographical Map Figure (USA) ---
    fig_geo = px.scatter_geo(
        df_geo,
        locations='state_code',
        locationmode="USA-states",
        size='total_sales',
        scope="usa",
        custom_data=['state_usa', 'total_sales']
    )
    fig_geo.update_traces(
        marker_color='#62738c',
        hovertemplate='<b>%{customdata[0]}</b><br>Total Sales: %{customdata[1]:$,.2f}<extra></extra>'
    )

    # --- Create Bar Chart Figure (Monthly Promo %) ---
    fig_bar = px.bar(
        monthly_summary,
        x='month',
        y='promo_percentage',
        text_auto='.1%',
        labels={'month': 'Month', 'promo_percentage': 'Promotional Sales %'}
    )
    fig_bar.update_yaxes(tickformat=".0%")
    fig_bar.update_traces(textangle=0, textposition="outside")

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

    # Create a figure with subplots
    fig_combined = make_subplots(
        rows=2, cols=2,
        specs=[[{'type': 'scattergeo'}, {'type': 'treemap', 'rowspan': 2}],
               [{'type': 'bar'}, None]],
        column_widths=[0.5, 0.5],
        row_heights=[0.6, 0.4],
        vertical_spacing=0.15
    )

    # Add geo traces
    for trace in fig_geo.data:
        fig_combined.add_trace(trace, row=1, col=1)

    # Add bar chart traces
    for trace in fig_bar.data:
        fig_combined.add_trace(trace, row=2, col=1)

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
        fig_combined.data[
            treemap_trace_index].hovertemplate = '<b>%{label}</b><br>Value:%{value}<br>Share of Parent: %{percentParent:.1%}<extra></extra>'
        fig_combined.data[treemap_trace_index].marker.pad = dict(t=2, l=2, r=2, b=2)

        # --- Update overall layout ---
        fig_combined.update_layout(
            # Manually create annotations to act as subplot titles
            annotations=[
                dict(
                    text="<b>Sales Distribution in the USA</b>",
                    y=1.0, x=0.25,
                    xref='paper', yref='paper',
                    font=dict(size=20), showarrow=False, xanchor='center', yanchor='bottom'
                ),
                dict(
                    text="<b>Product Distribution</b>",
                    y=1.0, x=0.75,
                    xref='paper', yref='paper',
                    font=dict(size=16), showarrow=False, xanchor='center', yanchor='bottom'
                ),
                dict(
                    text="<b>Promotional Sales % by Month</b>",
                    y=0.38, x=0.25,
                    xref='paper', yref='paper',
                    font=dict(size=16), showarrow=False, xanchor='center', yanchor='bottom'
                )
            ],
            legend=dict(
                orientation="h",
                yanchor="top",
                y=0.97,
                xanchor="center",
                x=0.75
            ),
            coloraxis_showscale=False,
            margin=dict(t=100, l=25, r=25, b=25),
            hoverlabel=dict(
                bgcolor="white",
                font_size=16,
                font_family="Rockwell"
            ),
            xaxis_visible=False,
            yaxis_visible=False,
            # Set the background color to white
            paper_bgcolor='white',
            plot_bgcolor='white'
        )

    # Configure the geographic map properties
    fig_combined.update_geos(
        scope='usa',
        landcolor='#d6d6d6',  # Set the land color for the states
        row=1, col=1
    )

    fig_combined.show()


if __name__ == "__main__":
    create_dashboard()