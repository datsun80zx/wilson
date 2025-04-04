import os
import pandas as pd

def generate_sales_conversion_report(consolidated_data, sales_file, output_dir=None, person=None, month=None):
    """
    Generate a report analyzing the percentage of Customer IDs from the
    consolidated activity file that also appear in the sales file (closing rate).
    
    Parameters:
    consolidated_data : pandas.DataFrame or str
        Either a DataFrame containing the consolidated data or a path to the CSV file
    sales_file : str
        Path to the sales CSV file
    output_dir : str, optional
        Directory to save report files. If None, reports are only returned as data
    person : str, optional
        Person name for report labeling
    month : str, optional
        Month for report labeling
    """
    # Load the files
    if isinstance(consolidated_data, str):
        consolidated_data = pd.read_csv(consolidated_data)
    
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
    
    # Create report prefix for filenames
    report_prefix = ""
    if person and month:
        report_prefix = f"{person}_month_{month}_"
    
    # Print report
    print("\n===== SALES CONVERSION REPORT =====")
    if person and month:
        print(f"Report for: {person} - Month {month}")
    print(f"Total unique customers in activity logs: {total_customers}")
    print(f"Customers who made a purchase: {converted_customers}")
    print(f"Conversion rate: {conversion_rate:.2f}%")
    print(f"Customers who did not convert: {total_customers - converted_customers}")
    
    # Only save files if output directory is specified
    if output_dir:
        # Generate a detailed CSV report
        # List of customers in consolidated but not in sales (non-converted)
        non_converted = consolidated_customers - sales_customers
        if non_converted:
            # Get records for non-converted customers
            non_converted_data = consolidated_data[
                consolidated_data[customer_id_col_consolidated].isin(non_converted)
            ].drop_duplicates(subset=[customer_id_col_consolidated])
            
            # Save to CSV
            non_converted_path = os.path.join(output_dir, f"{report_prefix}non_converted_customers.csv")
            non_converted_data.to_csv(non_converted_path, index=False)
            print(f"\nDetails of non-converted customers saved to '{non_converted_path}'")
        
        # List of customers in sales (converted)
        if converted_customers > 0:
            # Get records for converted customers
            converted_data = consolidated_data[
                consolidated_data[customer_id_col_consolidated].isin(sales_customers)
            ].drop_duplicates(subset=[customer_id_col_consolidated])
            
            # Save to CSV
            converted_path = os.path.join(output_dir, f"{report_prefix}converted_customers.csv")
            converted_data.to_csv(converted_path, index=False)
            print(f"Details of converted customers saved to '{converted_path}'")
        
        # Save full report as CSV
        report_df = pd.DataFrame([{
            "Person": person if person else "Unknown",
            "Month": month if month else "Unknown",
            "Total Customers": total_customers,
            "Converted Customers": converted_customers,
            "Conversion Rate (%)": round(conversion_rate, 2),
            "Non-Converted Customers": total_customers - converted_customers
        }])
        
        report_path = os.path.join(output_dir, f"{report_prefix}sales_conversion_report.csv")
        report_df.to_csv(report_path, index=False)
        print(f"Summary report saved to '{report_path}'")
    
    return {
        "person": person,
        "month": month,
        "total_customers": total_customers,
        "converted_customers": converted_customers,
        "conversion_rate": conversion_rate,
        "customers_not_converted": total_customers - converted_customers
    }

def generate_consolidated_reports(all_person_reports, base_output_dir):
    """
    Create consolidated reports across all people and months.
    
    Parameters:
    all_person_reports : list
        List of dictionaries containing report data from generate_sales_conversion_report
    base_output_dir : str
        Base directory to save consolidated reports
    """
    if not all_person_reports:
        print("No reports to consolidate.")
        return
    
    # Create a DataFrame from all reports
    all_reports_df = pd.DataFrame(all_person_reports)
    
    # Save the consolidated report
    consolidated_path = os.path.join(base_output_dir, "consolidated_sales_report.csv")
    all_reports_df.to_csv(consolidated_path, index=False)
    print(f"\nConsolidated report for all people and months saved to '{consolidated_path}'")
    
    # Create monthly reports (aggregate by month)
    monthly_reports = all_reports_df.groupby('month').agg({
        'total_customers': 'sum',
        'converted_customers': 'sum',
        'customers_not_converted': 'sum'
    }).reset_index()
    
    # Calculate conversion rates for each month
    monthly_reports['conversion_rate'] = (monthly_reports['converted_customers'] / 
                                         monthly_reports['total_customers'] * 100).round(2)
    
    # Save monthly reports
    monthly_path = os.path.join(base_output_dir, "monthly_sales_report.csv")
    monthly_reports.to_csv(monthly_path, index=False)
    print(f"Monthly consolidated report saved to '{monthly_path}'")
    
    # Create per-person reports (aggregate by person)
    person_reports = all_reports_df.groupby('person').agg({
        'total_customers': 'sum',
        'converted_customers': 'sum',
        'customers_not_converted': 'sum'
    }).reset_index()
    
    # Calculate conversion rates for each person
    person_reports['conversion_rate'] = (person_reports['converted_customers'] / 
                                        person_reports['total_customers'] * 100).round(2)
    
    # Save per-person reports
    person_path = os.path.join(base_output_dir, "person_sales_report.csv")
    person_reports.to_csv(person_path, index=False)
    print(f"Per-person consolidated report saved to '{person_path}'")
    
    return all_reports_df, monthly_reports, person_reports

# def generate_sales_conversion_report(consolidated_data, sales_file):
#     """
#     Generate a report analyzing the percentage of Customer IDs from the
#     consolidated activity file that also appear in the sales file (closing rate).
    
#     Parameters:
#     consolidated_data : pandas.DataFrame or str
#         Either a DataFrame containing the consolidated data or a path to the CSV file
#     sales_file : str
#         Path to the sales CSV file
#     """
#     # Load the files
#     if isinstance(consolidated_data, str):
#         consolidated_data = pd.read_csv(consolidated_data)
    
#     sales_data = pd.read_csv(sales_file)
    
#     # Print column names to verify
#     print("Columns in consolidated file:", consolidated_data.columns.tolist())
#     print("Columns in sales file:", sales_data.columns.tolist())
    
#     # Identify the Customer ID column in both files
#     # First, look for exact match in column names
#     customer_id_cols = [col for col in consolidated_data.columns if 'customer' in col.lower() and 'id' in col.lower()]
#     if customer_id_cols:
#         customer_id_col_consolidated = customer_id_cols[0]
#     else:
#         # If no exact match, look for anything with 'customer' in it
#         customer_id_cols = [col for col in consolidated_data.columns if 'customer' in col.lower()]
#         if customer_id_cols:
#             customer_id_col_consolidated = customer_id_cols[0]
#         else:
#             print("ERROR: Cannot find Customer ID column in consolidated file")
#             return {}
    
#     # Do the same for sales file
#     customer_id_cols = [col for col in sales_data.columns if 'customer' in col.lower() and 'id' in col.lower()]
#     if customer_id_cols:
#         customer_id_col_sales = customer_id_cols[0]
#     else:
#         customer_id_cols = [col for col in sales_data.columns if 'customer' in col.lower()]
#         if customer_id_cols:
#             customer_id_col_sales = customer_id_cols[0]
#         else:
#             print("ERROR: Cannot find Customer ID column in sales file")
#             return {}
    
#     print(f"Using '{customer_id_col_consolidated}' as Customer ID column in consolidated file")
#     print(f"Using '{customer_id_col_sales}' as Customer ID column in sales file")
    
#     # Get unique Customer IDs from both files
#     consolidated_customers = set(consolidated_data[customer_id_col_consolidated].unique())
#     sales_customers = set(sales_data[customer_id_col_sales].unique())

#     print(f"Unique Customers in Consolidated file: {len(consolidated_customers)}")
#     print(f"Unique Customers in Sales File: {len(sales_customers)}")
    
#     # Calculate metrics
#     total_customers = len(consolidated_customers)
#     converted_customers = len(consolidated_customers.intersection(sales_customers))
#     conversion_rate = (converted_customers / total_customers * 100) if total_customers > 0 else 0
    
#     # Print report
#     print("\n===== SALES CONVERSION REPORT =====")
#     print(f"Total unique customers in activity logs: {total_customers}")
#     print(f"Customers who made a purchase: {converted_customers}")
#     print(f"Conversion rate: {conversion_rate:.2f}%")
#     print(f"Customers who did not convert: {total_customers - converted_customers}")
    
#     # Generate a detailed CSV report
#     # List of customers in consolidated but not in sales (non-converted)
#     non_converted = consolidated_customers - sales_customers
#     if non_converted:
#         # Get records for non-converted customers
#         non_converted_data = consolidated_data[
#             consolidated_data[customer_id_col_consolidated].isin(non_converted)
#         ].drop_duplicates(subset=[customer_id_col_consolidated])
        
#         # Save to CSV
#         non_converted_data.to_csv('non_converted_customers.csv', index=False)
#         print(f"\nDetails of non-converted customers saved to 'non_converted_customers.csv'")
    
#     # List of customers in sales (converted)
#     if converted_customers > 0:
#         # Get records for converted customers
#         converted_data = consolidated_data[
#             consolidated_data[customer_id_col_consolidated].isin(sales_customers)
#         ].drop_duplicates(subset=[customer_id_col_consolidated])
        
#         # Save to CSV
#         converted_data.to_csv('converted_customers.csv', index=False)
#         print(f"Details of converted customers saved to 'converted_customers.csv'")
    
#     # Optional: Save full report as CSV
#     report_df = pd.DataFrame([{
#         "Total Customers": total_customers,
#         "Converted Customers": converted_customers,
#         "Conversion Rate (%)": round(conversion_rate, 2),
#         "Non-Converted Customers": total_customers - converted_customers
#     }])
#     report_df.to_csv('sales_conversion_report.csv', index=False)
#     print(f"Summary report saved to 'sales_conversion_report.csv'")
    
#     return {
#         "total_customers": total_customers,
#         "converted_customers": converted_customers,
#         "conversion_rate": conversion_rate,
#         "customers_not_converted": total_customers - converted_customers
#     }