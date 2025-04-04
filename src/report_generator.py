import os
import pandas as pd

def generate_sales_conversion_report(consolidated_data, sales_file, output_dir=None, person=None, month=None):
    """
    Generate a report analyzing the conversion rate of customers.
    Consider all customers in the sales file as converted.
    """
    # Load the files
    if isinstance(consolidated_data, str):
        consolidated_data = pd.read_csv(consolidated_data)
    
    sales_data = pd.read_csv(sales_file)
    
    # Print column names to verify
    print("Columns in consolidated file:", consolidated_data.columns.tolist())
    print("Columns in sales file:", sales_data.columns.tolist())
    
    # Find Job ID columns in both files
    job_id_columns = {
        'consolidated': None,
        'sales': None
    }
    
    # Customer ID columns in both files
    customer_id_columns = {
        'consolidated': None,
        'sales': None
    }
    
    # Find column names in both files
    for file_type, df in [('consolidated', consolidated_data), ('sales', sales_data)]:
        # Find Job ID column
        for col in df.columns:
            if col.lower() == 'job id':
                job_id_columns[file_type] = col
                break
        
        if job_id_columns[file_type] is None:
            possible_cols = [col for col in df.columns 
                            if 'job' in col.lower() and 'id' in col.lower()]
            if possible_cols:
                job_id_columns[file_type] = possible_cols[0]
        
        # Find Customer ID column
        for col in df.columns:
            if 'customer' in col.lower() and 'id' in col.lower():
                customer_id_columns[file_type] = col
                break
        
        if customer_id_columns[file_type] is None:
            possible_cols = [col for col in df.columns 
                            if 'customer' in col.lower()]
            if possible_cols:
                customer_id_columns[file_type] = possible_cols[0]
    
    # Verify we found all necessary columns
    if not job_id_columns['consolidated'] or not customer_id_columns['consolidated']:
        print("ERROR: Missing required columns in consolidated file")
        print(f"Job ID column: {job_id_columns['consolidated']}")
        print(f"Customer ID column: {customer_id_columns['consolidated']}")
        return {}
    
    if not job_id_columns['sales'] or not customer_id_columns['sales']:
        print("ERROR: Missing required columns in sales file")
        print(f"Job ID column: {job_id_columns['sales']}")
        print(f"Customer ID column: {customer_id_columns['sales']}")
        return {}
    
    print(f"Using '{job_id_columns['consolidated']}' as Job ID column in consolidated file")
    print(f"Using '{customer_id_columns['consolidated']}' as Customer ID column in consolidated file")
    print(f"Using '{job_id_columns['sales']}' as Job ID column in sales file")
    print(f"Using '{customer_id_columns['sales']}' as Customer ID column in sales file")
    
    # Fix all ID columns in both DataFrames
    for file_type, df in [('consolidated', consolidated_data), ('sales', sales_data)]:
        # Process Job ID column
        col = job_id_columns[file_type]
        if pd.api.types.is_numeric_dtype(df[col]):
            # If all values are integers (no decimal part)
            if df[col].dropna().apply(lambda x: x == int(x)).all():
                df[col] = df[col].fillna(-1).astype(int).astype(str)
                df[col] = df[col].replace('-1', '')
            else:
                df[col] = df[col].astype(str).str.strip()
        else:
            df[col] = df[col].astype(str).str.strip()
        
        # Process Customer ID column
        col = customer_id_columns[file_type]
        if pd.api.types.is_numeric_dtype(df[col]):
            # If all values are integers (no decimal part)
            if df[col].dropna().apply(lambda x: x == int(x)).all():
                df[col] = df[col].fillna(-1).astype(int).astype(str)
                df[col] = df[col].replace('-1', '')
            else:
                df[col] = df[col].astype(str).str.strip()
        else:
            df[col] = df[col].astype(str).str.strip()
    
    # Display sample job IDs and customer IDs from both files for debugging
    print("\nSample data from consolidated file:")
    print("Job IDs:", consolidated_data[job_id_columns['consolidated']].head(3).tolist())
    print("Customer IDs:", consolidated_data[customer_id_columns['consolidated']].head(3).tolist())
    
    print("\nSample data from sales file:")
    print("Job IDs:", sales_data[job_id_columns['sales']].head(3).tolist())
    print("Customer IDs:", sales_data[customer_id_columns['sales']].head(3).tolist())
    
    # Get unique Customer IDs from both files
    consolidated_customers = set(consolidated_data[customer_id_columns['consolidated']].unique())
    sales_customers = set(sales_data[customer_id_columns['sales']].unique())

    print(f"\nUnique Customers in Consolidated file: {len(consolidated_customers)}")
    print(f"Unique Customers in Sales File: {len(sales_customers)}")
    
    # FIXED: All customers in sales file made a purchase
    # Consider all sales customers as converted
    # We'll still find the matching customers to identify which consolidated customers converted
    matching_customers = sales_customers.intersection(consolidated_customers)
    
    # Consider customers who appear in the sales file but not in consolidated data
    sales_only_customers = sales_customers - consolidated_customers
    if sales_only_customers:
        print(f"WARNING: {len(sales_only_customers)} customers in sales file do not appear in activity logs")
        if len(sales_only_customers) > 0:
            print(f"Sample customers only in sales file: {list(sales_only_customers)[:3]}")
    
    # Calculate metrics
    total_customers = len(consolidated_customers)
    converted_customers = len(matching_customers)  # These are customers that appear in both files
    all_sold_customers = len(sales_customers)  # All customers who made a purchase
    
    # FIXED: Calculate conversion rate based on ALL customers in sales file
    # This includes both matching customers and sales-only customers
    conversion_rate = (all_sold_customers / total_customers * 100) if total_customers > 0 else 0
    
    # Create report prefix for filenames
    report_prefix = ""
    if person and month:
        report_prefix = f"{person}_month_{month}_"
    
    # Print report
    print("\n===== SALES CONVERSION REPORT =====")
    if person and month:
        print(f"Report for: {person} - Month {month}")
    print(f"Total unique customers in activity logs: {total_customers}")
    print(f"Customers who made a purchase and appear in activity logs: {converted_customers}")
    print(f"Total customers who made a purchase (all sales): {all_sold_customers}")
    print(f"Conversion rate (all sales / all customers): {conversion_rate:.2f}%")
    print(f"Customers who did not convert: {total_customers - converted_customers}")
    print(f"Sales customers not in activity logs: {len(sales_only_customers)}")
    
    # Only save files if output directory is specified
    if output_dir:
        # Generate a detailed CSV report
        # List of customers in consolidated but not in sales (non-converted)
        non_converted = consolidated_customers - sales_customers
        if non_converted:
            # Get records for non-converted customers
            non_converted_data = consolidated_data[
                consolidated_data[customer_id_columns['consolidated']].isin(non_converted)
            ].drop_duplicates(subset=[customer_id_columns['consolidated']])
            
            # Save to CSV
            non_converted_path = os.path.join(output_dir, f"{report_prefix}non_converted_customers.csv")
            non_converted_data.to_csv(non_converted_path, index=False)
            print(f"\nDetails of non-converted customers saved to '{non_converted_path}'")
        
        # List of customers in sales that are also in consolidated (converted)
        if converted_customers > 0:
            # Get records for converted customers
            converted_data = consolidated_data[
                consolidated_data[customer_id_columns['consolidated']].isin(matching_customers)
            ].drop_duplicates(subset=[customer_id_columns['consolidated']])
            
            # Save to CSV
            converted_path = os.path.join(output_dir, f"{report_prefix}converted_customers.csv")
            converted_data.to_csv(converted_path, index=False)
            print(f"Details of converted customers saved to '{converted_path}'")
        
        # For sales customers not in activity logs, save them separately
        if sales_only_customers:
            sales_only_data = sales_data[
                sales_data[customer_id_columns['sales']].isin(sales_only_customers)
            ].drop_duplicates(subset=[customer_id_columns['sales']])
            
            sales_only_path = os.path.join(output_dir, f"{report_prefix}sales_only_customers.csv")
            sales_only_data.to_csv(sales_only_path, index=False)
            print(f"Details of sales customers not in activity logs saved to '{sales_only_path}'")
        
        # Save full report as CSV
        report_df = pd.DataFrame([{
            "Person": person if person else "Unknown",
            "Month": month if month else "Unknown",
            "Total Customers": total_customers,
            "Customers in Both Files": converted_customers,
            "All Sales Customers": all_sold_customers,
            "Conversion Rate (%)": round(conversion_rate, 2),
            "Non-Converted Customers": total_customers - converted_customers,
            "Sales Only Customers": len(sales_only_customers)
        }])
        
        report_path = os.path.join(output_dir, f"{report_prefix}sales_conversion_report.csv")
        report_df.to_csv(report_path, index=False)
        print(f"Summary report saved to '{report_path}'")
    
    return {
        "person": person,
        "month": month,
        "total_customers": total_customers,
        "converted_customers": converted_customers,
        "all_sales_customers": all_sold_customers,
        "conversion_rate": conversion_rate,
        "customers_not_converted": total_customers - converted_customers,
        "sales_only_customers": len(sales_only_customers)
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
        'all_sales_customers': 'sum',
        'customers_not_converted': 'sum',
        'sales_only_customers': 'sum'
    }).reset_index()
    
    # Calculate conversion rates for each month - based on all sales customers
    monthly_reports['conversion_rate'] = (monthly_reports['all_sales_customers'] / 
                                         monthly_reports['total_customers'] * 100).round(2)
    
    # Save monthly reports
    monthly_path = os.path.join(base_output_dir, "monthly_sales_report.csv")
    monthly_reports.to_csv(monthly_path, index=False)
    print(f"Monthly consolidated report saved to '{monthly_path}'")
    
    # Create per-person reports (aggregate by person)
    person_reports = all_reports_df.groupby('person').agg({
        'total_customers': 'sum',
        'converted_customers': 'sum',
        'all_sales_customers': 'sum',
        'customers_not_converted': 'sum',
        'sales_only_customers': 'sum'
    }).reset_index()
    
    # Calculate conversion rates for each person - based on all sales customers
    person_reports['conversion_rate'] = (person_reports['all_sales_customers'] / 
                                        person_reports['total_customers'] * 100).round(2)
    
    # Save per-person reports
    person_path = os.path.join(base_output_dir, "person_sales_report.csv")
    person_reports.to_csv(person_path, index=False)
    print(f"Per-person consolidated report saved to '{person_path}'")
    
    return all_reports_df, monthly_reports, person_reports