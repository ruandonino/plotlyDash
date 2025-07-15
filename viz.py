import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def create_product_treemap():
    # Read the products data
    # Using a dummy dataframe for demonstration as the CSV is not available
    try:
        df = pd.read_csv('../data/products.csv')
    except FileNotFoundError:
        print("CSV file not found. Using dummy data.")
        data = {
            'category': ['Electronics', 'Electronics', 'Furniture', 'Furniture', 'Home Appliances', 'Home Appliances', 'Sports', 'Clothing'],
            'sub_category': ['Laptops', 'Smartphones', 'Chairs', 'Tables', 'Refrigerators', 'Microwaves', 'Bicycles', 'Shirts'],
            'value': [1500, 1200, 300, 500, 800, 200, 600, 150]
        }
        df = pd.DataFrame(data)

    # Define the color map to be used
    color_map = {
         'Home Appliances': '#d8d8d8',
         'Electronics': '#5a6d8b',
         'Sports': '#66bfc7',
         'Furniture': '#a14df2',
         'Clothing': '#3333a6'
     }

    # Create treemap
    fig = px.treemap(df,
                     path=['category', 'sub_category'],
                     values='value',
                     color='category',
                     color_discrete_map=color_map,
                     title='Product Distribution by Category and Subcategory'
                     )

    # Add invisible traces for the legend
    for category_name, color in color_map.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=15, color=color),
            name=category_name,
            showlegend=True
        ))

    # All the logic for manipulating the treemap trace remains the same
    # ... (code for percentages, hiding parent categories, etc.)
    category_totals = df.groupby('category')['value'].sum()
    subcategory_percentages = []
    for subcat in df['sub_category'].unique():
        category = df[df['sub_category'] == subcat]['category'].iloc[0]
        subcat_total = df[df['sub_category'] == subcat]['value'].sum()
        cat_total = category_totals[category]
        percentage = (subcat_total / cat_total) * 100
        subcategory_percentages.append(f"{percentage:.1f}%")
    subcat_to_percentage = dict(zip(df['sub_category'].unique(), subcategory_percentages))
    for trace in fig.data:
        if trace.type != 'treemap': continue
        trace.textinfo = 'label+value+percent parent'
        trace.texttemplate = "<b>%{label}</b><br><b>%{value}</b><br><b>%{percentParent:.1%}</b>"
        custom_text = []; colors = []
        trace_percentages = []
        for label in trace.labels:
            if label in df['category'].unique(): trace_percentages.append('')
            else:
                if label in subcat_to_percentage: trace_percentages.append(subcat_to_percentage[label])
                else: trace_percentages.append('0.0%')
        for i, (label, color) in enumerate(zip(trace.labels, trace.marker.colors)):
            if label in df['category'].unique():
                custom_text.append(''); trace.labels[i] = ''; colors.append('white')
            else: colors.append(color)
        trace.marker.colors = colors
        trace.hovertemplate = [f'<b>%{{label}}</b><br>Value: %{{value}}<br>Percentage: {percentage}<extra></extra>' if label not in df['category'].unique() else '<extra></extra>' for label, percentage in zip(trace.labels, trace_percentages)]
        trace.marker.line.width = [0 if label == '' else 1 for label in trace.labels]
        trace.marker.line.color = 'white'


    # Update layout to align title and legend to the top-left
    fig.update_layout(
        # Position title at the top-left
        title_x=0.02,
        title_y=0.85,

        # --- MODIFIED LEGEND SETTINGS ---
        legend=dict(
            # Change orientation back to horizontal
            orientation="h",
            # Position legend just below the title, on the left
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.0
        ),
        # ---------------------------------

        xaxis_visible=False,
        yaxis_visible=False,
        margin=dict(t=120, l=25, r=25, b=25),
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Rockwell"
        )
    )

    # Show the figure
    fig.show()


if __name__ == "__main__":
    create_product_treemap()