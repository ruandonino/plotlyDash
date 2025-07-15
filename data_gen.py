import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)

# Constants for product data
PRODUCT_CATEGORIES = {
    'Electronics': ['Smartphones', 'Laptops', 'Tablets', 'Headphones', 'Smartwatches'],
    'Furniture': ['Chairs', 'Tables', 'Sofas', 'Desks', 'Cabinets'],
    'Clothing': ['Shirts', 'Pants', 'Dresses', 'Jackets', 'Shoes'],
    'Home Appliances': ['Refrigerators', 'Washing Machines', 'Microwaves', 'Blenders', 'Toasters'],
    'Sports': ['Bicycles', 'Treadmills', 'Dumbbells', 'Yoga Mats', 'Sportswear']
}

STATES_USA = [
    'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
    'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
    'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan',
    'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
    'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma',
    'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee',
    'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
]


def generate_product_data(num_products=150):
    """Generate product sales data."""
    products = []

    # Generate product IDs
    product_ids = [f'P{str(i + 1).zfill(3)}' for i in range(num_products)]

    # Generate categories and subcategories
    categories = []
    subcategories = []
    for _ in range(num_products):
        category = np.random.choice(list(PRODUCT_CATEGORIES.keys()))
        subcategory = np.random.choice(PRODUCT_CATEGORIES[category])
        categories.append(category)
        subcategories.append(subcategory)

    # Generate values with different ranges based on category
    values = []
    for cat in categories:
        if cat == 'Electronics':
            values.append(round(np.random.uniform(100, 2000), 2))
        elif cat == 'Furniture':
            values.append(round(np.random.uniform(50, 1500), 2))
        elif cat == 'Clothing':
            values.append(round(np.random.uniform(10, 200), 2))
        elif cat == 'Home Appliances':
            values.append(round(np.random.uniform(80, 2500), 2))
        else:  # Sports
            values.append(round(np.random.uniform(30, 1200), 2))

    # Create DataFrame
    df = pd.DataFrame({
        'product_id': product_ids,
        'category': categories,
        'sub_category': subcategories,
        'value': values
    })

    return df


def generate_sales_summary(year=2023, num_months=12, num_states=20):
    """Generate monthly sales summary data."""
    months = []
    years = []
    total_costs = []
    total_discounts = []
    order_avgs = []
    units_sold = []
    profit_margins = []
    total_sales = []
    states = []

    # Select random states
    selected_states = np.random.choice(STATES_USA, size=num_states, replace=False)

    for month in range(1, num_months + 1):
        for state in selected_states[:num_states]:
            # Base values with some randomness
            base_sales = np.random.uniform(50000, 200000)
            seasonality = 1 + 0.2 * np.sin((month - 1) * np.pi / 6)  # Seasonal pattern

            # Generate metrics
            total_cost = round(base_sales * np.random.uniform(0.5, 0.8) * seasonality, 2)
            total_discount = round(total_cost * np.random.uniform(0.01, 0.15), 2)
            order_avg = round(np.random.uniform(50, 300), 2)
            units = int(base_sales * np.random.uniform(0.5, 2.0) / order_avg)
            profit_margin = round(np.random.uniform(0.1, 0.4), 2)
            sales = round(total_cost / (1 - profit_margin), 2)

            # Add to lists
            months.append(month)
            years.append(year)
            total_costs.append(total_cost)
            total_discounts.append(total_discount)
            order_avgs.append(order_avg)
            units_sold.append(units)
            profit_margins.append(profit_margin)
            total_sales.append(sales)
            states.append(state)

    # Calculate percentage of promotional vs non-promotional sales
    promo_percent = [round(np.random.uniform(0.2, 0.6), 2) for _ in range(len(months))]
    non_promo_percent = [round(1 - p, 2) for p in promo_percent]

    # Create DataFrame
    df = pd.DataFrame({
        'month': months,
        'year': years,
        'total_cost': total_costs,
        'total_discount': total_discounts,
        'order_avg': order_avgs,
        'units_sales': units_sold,
        'profit_margin': profit_margins,
        'total_sales': total_sales,
        'state_usa': states,
        'percentage_promo': promo_percent,
        'percentage_non_promo': non_promo_percent
    })

    # Ensure we have exactly 100 rows
    return df.head(100) if len(df) >= 100 else df


def save_datasets(products_df, sales_df, output_dir='data'):
    """Save the generated datasets to CSV files."""
    output_path = '../data'
    #output_path.mkdir(exist_ok=True)

    products_path = output_path + '/products.csv'
    sales_path = output_path + '/sales_summary.csv'

    products_df.to_csv(products_path, index=False)
    sales_df.to_csv(sales_path, index=False)

    print(f"Datasets saved to:\n- {products_path}\n- {sales_path}")


def main():
    print("Generating product data...")
    products_df = generate_product_data(150)

    print("Generating sales summary data...")
    sales_df = generate_sales_summary(year=2023)

    print("\nDataset Summary:")
    print(f"Total products: {len(products_df)}")
    print(f"Total sales records: {len(sales_df)}")
    print(f"Date range: {sales_df['month'].min()}/2023 to {sales_df['month'].max()}/2023")
    print(f"Total sales value: ${sales_df['total_sales'].sum():,.2f}")

    # Save datasets
    save_datasets(products_df, sales_df)

    # Print sample data
    print("\nSample Product Data:")
    print(products_df.head(5).to_string(index=False))
    print("\nSample Sales Summary Data:")
    print(sales_df.head(3).to_string(index=False))


if __name__ == "__main__":
    main()