import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path


def create_dashboard():
    # ==============================================================================
    # 1. DATA PREPARATION
    # ==============================================================================

    # --- Construct robust paths for data and output directories ---
    try:
        # Get the directory of the script file
        script_dir = Path(__file__).resolve().parent
        # The base directory is the parent of the 'scripts' directory
        base_dir = script_dir.parent
    except NameError:
        # Fallback for environments where __file__ is not defined (e.g., some notebooks)
        base_dir = Path('.')

    data_dir = base_dir / 'data'
    outputs_dir = base_dir / 'outputs'
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
        # NOTE: Added all required columns to the dummy data to prevent errors.
        sales_data = {
            'state_usa': ['California', 'Texas', 'Florida', 'New York', 'Pennsylvania',
                          'Illinois', 'Ohio', 'Georgia', 'North Carolina', 'Michigan'],
            'total_sales': [125000, 180000, 150000, 140000, 90000, 110000, 85000, 95000, 78000, 70000],
            'order_avg': [150, 160, 155, 170, 145, 150, 140, 148, 130, 135],
            'total_cost': [80000, 110000, 95000, 90000, 60000, 70000, 55000, 65000, 50000, 48000],
            'total_discount': [12000, 15000, 13000, 14000, 9000, 11000, 8000, 9000, 7000, 6000],
            'units_sales': [800, 1100, 950, 850, 600, 720, 600, 650, 580, 500],
            'percentage_promo': [0.1, 0.15, 0.12, 0.2, 0.08, 0.1, 0.11, 0.13, 0.09, 0.07],
            'year': [2023, 2023, 2023, 2024, 2024, 2024, 2024, 2024, 2024, 2024],
            'month': [10, 11, 12, 1, 2, 3, 4, 5, 6, 7]
        }
        df_sales = pd.DataFrame(sales_data)

    # Aggregate sales data by state
    df_geo = df_sales.groupby('state_usa')['total_sales'].sum().reset_index()

    # --- Data for KPIs/Cards ---
    # Calculate an estimated order count to derive average order value
    df_sales['order_count_est'] = df_sales['total_sales'] / df_sales['order_avg']
    total_order_count = df_sales['order_count_est'].sum()
    total_revenue = df_sales['total_sales'].sum()
    total_cost = df_sales['total_cost'].sum()

    # Calculate high-level metrics
    total_profit = total_revenue - total_cost
    total_discount = df_sales['total_discount'].sum()
    profit_margin = total_profit / total_revenue if total_revenue else 0
    avg_order_value = total_revenue / total_order_count if total_order_count else 0
    total_units = df_sales['units_sales'].sum()

    # Product-specific KPIs
    num_products = len(df_products)

    # --- Data for Bar Chart (Monthly Promotional Sales Percentage) ---
    df_bar = df_sales.copy()
    # Calculate promotional sales for each record
    df_bar['promo_sales'] = df_bar['total_sales'] * df_bar['percentage_promo']
    # Group by month and sum total sales and promo sales
    monthly_summary = df_bar.groupby(['year', 'month']).agg(
        total_sales=('total_sales', 'sum'),
        promo_sales=('promo_sales', 'sum')
    ).reset_index()
    # Calculate the overall promotional percentage for the month
    monthly_summary['promo_percentage'] = (monthly_summary['promo_sales'] / monthly_summary['total_sales'])

    # Create a month-year label for the x-axis
    month_map = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    monthly_summary['month_name'] = monthly_summary['month'].map(month_map)
    monthly_summary['month_year_label'] = monthly_summary['month_name'] + ' ' + monthly_summary['year'].astype(str)

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
    fig_bar = go.Figure()

    fig_bar.add_trace(go.Bar(
        x=monthly_summary['month_year_label'],
        y=[1] * len(monthly_summary),
        marker_color='lightgray',
        hoverinfo='none',
        showlegend=False
    ))

    fig_bar.add_trace(go.Bar(
        x=monthly_summary['month_year_label'],
        y=monthly_summary['promo_percentage'],
        hovertemplate='Promotional Sales: %{y:.1%}<extra></extra>',
        marker_color='#62738c',
        showlegend=False
    ))

    fig_bar.update_layout(showlegend=False)

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
        rows=3, cols=2,
        specs=[[{'type': 'indicator', 'colspan': 2}, None],
               [{'type': 'scattergeo'}, {'type': 'treemap', 'rowspan': 2}],
               [{'type': 'bar'}, None]],
        column_widths=[0.5, 0.5],
        # ================== FIX 1: START ==================
        # Change row heights to push the charts down, creating more header space.
        row_heights=[0.10, 0.55, 0.35],
        # =================== FIX 1: END ===================
        vertical_spacing=0.15,
        horizontal_spacing=0.04
    )

    # --- Add Indicator (KPI) Traces ---
    indicators_data = [
        {'text': 'KPIs', 'title': ''},
        {'title': "Net Revenue", 'value': total_revenue, 'prefix': '$', 'valueformat': ',.0f'},
        {'title': "Profit", 'value': total_profit, 'prefix': '$', 'valueformat': ',.0f'},
        {'title': "Discount", 'value': total_discount, 'prefix': '$', 'valueformat': ',.0f'},
        {'title': "Profit Margin %", 'value': profit_margin, 'valueformat': '.1%'},
        {'title': "Order Count", 'value': total_order_count, 'valueformat': ',.0f'},
        {'title': "Order Value Avg", 'value': avg_order_value, 'prefix': '$', 'valueformat': ',.0f'},
        {'title': "Units (# of)", 'value': total_units, 'valueformat': ',.0f'},
        {'title': "Qty", 'value': num_products, 'valueformat': ',.0f'}
    ]


    x_start = 0.01
    num_cards = len(indicators_data)
    gap = 0.015
    total_gap_space = (num_cards - 1) * gap
    card_width = (1.0 - x_start * 2 - total_gap_space) / num_cards

    # We will collect all annotations here and add them to the layout at the end.
    # This prevents `update_layout` from overwriting annotations added with `add_annotation`.
    all_annotations = []

    # Add KPI cards. We use go.Indicator for numbers and a go.layout.Annotation for the text-only card.
    # This is a more robust approach than trying to force text into a numeric indicator.
    for ind,i in zip(indicators_data, range(len(indicators_data))):
        if 'text' in ind:
            # For the text-only card, we use an annotation positioned in the first slot.
            kpi_annotation = dict(
                text=f"<b>{ind['text']}</b><br><span style='font-size:12px;color:black'>{ind['title']}</span>",
                align='left',
                showarrow=False,
                xref='paper', yref='paper',
                x=x_start + 0.01, y=1,  # Position horizontally and vertically
                xanchor='left', yanchor='top',
                font=dict(size=20, color="black")  # Match the font size of the numeric KPIs
            )
            all_annotations.append(kpi_annotation)
        else:
            # For all numeric KPIs, we use a standard indicator trace.
            number_config = {
                'prefix': f"<b>{ind.get('prefix', '')}",
                'suffix': f"</b>{ind.get('suffix', '')}<br><span style='font-size:12px;color:black'>{ind['title']}</span>",
                'valueformat': ind.get('valueformat', ',.0f'),
                'font': {"size": 20, "color": "black"}
            }
            if(x_start + card_width > 1.0):
                card_width = 1.0 - x_start
            fig_combined.add_trace(go.Indicator(
                mode="number",
                value=ind['value'],
                number=number_config,
                domain={'row': 0, 'column': 0, 'x': [x_start, x_start + card_width], 'y': [0.95, 1]}
            ))
        # Increment the horizontal position for the next card
        if(i in [1,2]):
            x_start += (card_width + gap) + 0.02
        else:
            x_start += card_width + gap

    # Add geo traces
    for trace in fig_geo.data:
        fig_combined.add_trace(trace, row=2, col=1)

    # Add bar chart traces
    for trace in fig_bar.data:
        fig_combined.add_trace(trace, row=3, col=1)

    # Add treemap and legend traces
    for trace in fig_treemap.data:
        if trace.type == 'treemap':
            fig_combined.add_trace(trace, row=2, col=2)
        elif trace.type == 'scatter':
            fig_combined.add_trace(trace)

    # ==============================================================================
    # 4. UPDATE LAYOUT AND STYLING
    # ==============================================================================

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

    # --- Define annotations for chart titles and combine with KPI annotation ---
    chart_title_annotations = [
        dict(
            text="Map of Sales",
            y=0.84, x=0.055,  # Centered over the first column
            xref='paper', yref='paper',
            font=dict(size=16), showarrow=False, xanchor='center', yanchor='bottom'
        ),
        dict(
            text="Net Revenue by Subcategory",
            y=0.84, x=0.61,  # Centered over the second column
            xref='paper', yref='paper',
            font=dict(size=16), showarrow=False, xanchor='center', yanchor='bottom'
        ),
        dict(
            # Colored the word "Promo" to match the bar color for better visual association.
            text="% Net Revenue - <b style='color:#62738c'>Promo</b> vs <b>Non-Promo</b>",
            y=0.28, x=0.13,  # Centered over the first column
            xref='paper', yref='paper',
            font=dict(size=16), showarrow=False, xanchor='center', yanchor='bottom'
        )
    ]
    all_annotations.extend(chart_title_annotations)

    # --- Update overall layout ---
    fig_combined.update_layout(
        title_text="<b>Executive Sales Summary</b>",
        title_x=0.06,
        title_font_size=24,
        barmode='overlay',
        shapes=[
            dict(type="rect", xref="paper", yref="paper", x0=-0.05, y0=0.90, x1=1.03, y1=1.01,
                 fillcolor="#f5f5f5", line_width=0, layer="below"),
        ],
        annotations=all_annotations,
        # ================== FIX 2: START ==================
        # Move the legend up to sit neatly under its title
        legend=dict(
            orientation="h",
            yanchor="top",
            y=0.83,
            xanchor="center",
            x=0.71
        ),
        # =================== FIX 2: END ===================
        coloraxis_showscale=False,
        margin=dict(t=60, l=25, r=25, b=10),
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Rockwell"
        ),
        xaxis_visible=False,
        yaxis_visible=False,
        paper_bgcolor='white',
        plot_bgcolor='white'
    )

    # Configure the geographic map properties
    fig_combined.update_geos(
        scope='usa',
        landcolor='#d6d6d6',
        row=2, col=1,
        bgcolor='rgba(0,0,0,0)'
    )

    # --- Configure Bar Chart Axes ---
    fig_combined.update_xaxes(title_text="", visible=True, tickangle=-90, row=3, col=1)
    fig_combined.update_yaxes(
        title_text="Promotional Sales %",
        tickformat=".0%",
        visible=True,
        row=3,
        col=1
    )

    # --- Save the combined figure to an HTML file ---
    outputs_dir.mkdir(parents=True, exist_ok=True)
    output_file_path = outputs_dir / 'executive_sales_summary.html'
    fig_combined.write_html(output_file_path)
    print(f"Dashboard successfully saved to:\n{output_file_path.resolve()}")


if __name__ == "__main__":
    create_dashboard()