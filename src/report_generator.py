import pandas as pd

def generate_sales_conversion_report(consolidated_file, sales_file):
    """
    Generate a report analyzing the percentage of Customer IDs from the
    consolidated activity file that also appear in the sales file (closing rate).
    """
    # Load the files
    consolidated_data = pd.read_csv(consolidated_file)
    sales_data = pd.read_csv(sales_file)
    
    # Print column names to verify
    print("Columns in consolidated file:", consolidated_data.columns.tolist())
    print("Columns in sales file:", sales_data.columns.tolist())
    
    # Identify the Customer ID column in both files
    # First, look for exact match in column names
    customer_id_cols = [col for col in consolidated_data.columns if 'customer' in col.lower() and 'id' in col.lower()]
    if customer_id_cols:
        customer_id_col_consolidated = customer_id_cols[0]
    else:
        # If no exact match, look for anything with 'customer' in it
        customer_id_cols = [col for col in consolidated_data.columns if 'customer' in col.lower()]
        if customer_id_cols:
            customer_id_col_consolidated = customer_id_cols[0]
        else:
            print("ERROR: Cannot find Customer ID column in consolidated file")
            return {}
    
    # Do the same for sales file
    customer_id_cols = [col for col in sales_data.columns if 'customer' in col.lower() and 'id' in col.lower()]
    if customer_id_cols:
        customer_id_col_sales = customer_id_cols[0]
    else:
        customer_id_cols = [col for col in sales_data.columns if 'customer' in col.lower()]
        if customer_id_cols:
            customer_id_col_sales = customer_id_cols[0]
        else:
            print("ERROR: Cannot find Customer ID column in sales file")
            return {}
    
    print(f"Using '{customer_id_col_consolidated}' as Customer ID column in consolidated file")
    print(f"Using '{customer_id_col_sales}' as Customer ID column in sales file")
    
    # Get unique Customer IDs from both files
    consolidated_customers = set(consolidated_data[customer_id_col_consolidated].unique())
    sales_customers = set(sales_data[customer_id_col_sales].unique())

    print(f"Unique Customers in Consolidated file: {len(consolidated_customers)}")
    print(f"Unique Customers in Sales File: {len(sales_customers)}")
    
    # Calculate metrics
    total_customers = len(consolidated_customers)
    converted_customers = len(consolidated_customers.intersection(sales_customers))
    conversion_rate = (converted_customers / total_customers * 100) if total_customers > 0 else 0
    
    # Print report
    print("\n===== SALES CONVERSION REPORT =====")
    print(f"Total unique customers in activity logs: {total_customers}")
    print(f"Customers who made a purchase: {converted_customers}")
    print(f"Conversion rate: {conversion_rate:.2f}%")
    print(f"Customers who did not convert: {total_customers - converted_customers}")
    
    # Generate a detailed CSV report
    # List of customers in consolidated but not in sales (non-converted)
    non_converted = consolidated_customers - sales_customers
    if non_converted:
        # Get records for non-converted customers
        non_converted_data = consolidated_data[
            consolidated_data[customer_id_col_consolidated].isin(non_converted)
        ].drop_duplicates(subset=[customer_id_col_consolidated])
        
        # Save to CSV
        non_converted_data.to_csv('non_converted_customers.csv', index=False)
        print(f"\nDetails of non-converted customers saved to 'non_converted_customers.csv'")
    
    # List of customers in sales (converted)
    if converted_customers > 0:
        # Get records for converted customers
        converted_data = consolidated_data[
            consolidated_data[customer_id_col_consolidated].isin(sales_customers)
        ].drop_duplicates(subset=[customer_id_col_consolidated])
        
        # Save to CSV
        converted_data.to_csv('converted_customers.csv', index=False)
        print(f"Details of converted customers saved to 'converted_customers.csv'")
    
    # Optional: Save full report as CSV
    report_df = pd.DataFrame([{
        "Total Customers": total_customers,
        "Converted Customers": converted_customers,
        "Conversion Rate (%)": round(conversion_rate, 2),
        "Non-Converted Customers": total_customers - converted_customers
    }])
    report_df.to_csv('sales_conversion_report.csv', index=False)
    print(f"Summary report saved to 'sales_conversion_report.csv'")
    
    return {
        "total_customers": total_customers,
        "converted_customers": converted_customers,
        "conversion_rate": conversion_rate,
        "customers_not_converted": total_customers - converted_customers
    }