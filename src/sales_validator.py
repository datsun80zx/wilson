import pandas as pd

def validate_sales_in_activity(consolidated_data, sales_file):
    """
    Check if all Job IDs in the sales file are present in the consolidated activity file.
    
    Parameters:
    consolidated_data : pandas.DataFrame or str
        Either a DataFrame containing the consolidated data or a path to the CSV file
    sales_file : str
        Path to the sales CSV file
    """
    # Load the files
    if isinstance(consolidated_data, str):
        consolidated_data = pd.read_csv(consolidated_data)
    
    sales_data = pd.read_csv(sales_file)
    
    # Debug: Print column names to identify the correct job ID column
    print("Columns in consolidated file:", consolidated_data.columns.tolist())
    print("Columns in sales file:", sales_data.columns.tolist())
    
    # Try to identify the job ID column in the sales file
    job_id_column_consolidated = 'Job ID'  # Column in consolidated file
    
    # Look for possible job ID columns in sales file
    possible_job_columns = [col for col in sales_data.columns 
                          if 'job' in col.lower() or 'id' in col.lower()]
    
    if not possible_job_columns:
        print("ERROR: Cannot find a job ID column in the sales file.")
        print("Please check your sales file or specify the correct column name.")
        return False, []
    
    job_id_column_sales = possible_job_columns[0]
    print(f"Using '{job_id_column_sales}' as the job ID column in sales file")
    
    # Get unique Job IDs from both files
    consolidated_jobs = set(consolidated_data[job_id_column_consolidated].unique())
    sales_jobs = set(sales_data[job_id_column_sales].unique())
    
    # Find missing jobs (in sales but not in consolidated data)
    missing_jobs = sales_jobs - consolidated_jobs
    
    # Print results
    print(f"Total unique jobs in consolidated data: {len(consolidated_jobs)}")
    print(f"Total unique jobs in sales data: {len(sales_jobs)}")
    
    if missing_jobs:
        print(f"WARNING: {len(missing_jobs)} sales jobs are NOT in the consolidated activity list.")
        print("Missing Job IDs:")
        for job in sorted(list(missing_jobs))[:20]:  # Show first 20 to avoid flooding the console
            print(f"  - {job}")
        if len(missing_jobs) > 20:
            print(f"  ... and {len(missing_jobs) - 20} more")
        is_complete = False
    else:
        print("SUCCESS: All sales jobs are present in the consolidated activity list.")
        is_complete = True
    
    # Create a report of the missing jobs with any available details
    if missing_jobs:
        missing_details = sales_data[sales_data[job_id_column_sales].isin(missing_jobs)]
        missing_details.to_csv('missing_sales_jobs.csv', index=False)
        print(f"Details of missing jobs saved to 'missing_sales_jobs.csv'")
    
    return is_complete, list(missing_jobs)