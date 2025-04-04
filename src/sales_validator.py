import pandas as pd

def validate_sales_in_activity(consolidated_data, sales_file):
    """
    Check if all Job IDs in the sales file are present in the consolidated activity file.
    """
    # Load the files
    if isinstance(consolidated_data, str):
        consolidated_data = pd.read_csv(consolidated_data)
    
    sales_data = pd.read_csv(sales_file)
    
    # Print column names to identify the correct job ID column
    print("Columns in consolidated file:", consolidated_data.columns.tolist())
    print("Columns in sales file:", sales_data.columns.tolist())
    
    # Try to identify the job ID column in both files
    job_id_columns = {
        'consolidated': None,
        'sales': None
    }
    
    # Look for exact match 'Job ID' first
    for file_type, df in [('consolidated', consolidated_data), ('sales', sales_data)]:
        for col in df.columns:
            if col.lower() == 'job id':
                job_id_columns[file_type] = col
                break
        
        # If not found, look for columns with 'job' and 'id'
        if job_id_columns[file_type] is None:
            possible_cols = [col for col in df.columns 
                            if 'job' in col.lower() and 'id' in col.lower()]
            if possible_cols:
                job_id_columns[file_type] = possible_cols[0]
    
    # Ensure we found columns in both files
    if job_id_columns['consolidated'] is None:
        print("ERROR: Cannot find a job ID column in the consolidated file.")
        return False, []
    
    if job_id_columns['sales'] is None:
        print("ERROR: Cannot find a job ID column in the sales file.")
        return False, []
    
    print(f"Using '{job_id_columns['consolidated']}' as the job ID column in consolidated file")
    print(f"Using '{job_id_columns['sales']}' as the job ID column in sales file")
    
    # Fix integer-like float values (remove decimal points)
    for file_type, df in [('consolidated', consolidated_data), ('sales', sales_data)]:
        col = job_id_columns[file_type]
        if pd.api.types.is_numeric_dtype(df[col]):
            # Check if all values are integers (no decimal part)
            if df[col].dropna().apply(lambda x: x == int(x)).all():
                df[col] = df[col].fillna(-1).astype(int).astype(str)
                df[col] = df[col].replace('-1', '')
            else:
                df[col] = df[col].astype(str).str.strip()
        else:
            df[col] = df[col].astype(str).str.strip()
    
    # Display sample job IDs from both files for debugging
    print("\nSample job IDs from consolidated data:", consolidated_data[job_id_columns['consolidated']].head(3).tolist())
    print("Sample job IDs from sales data:", sales_data[job_id_columns['sales']].head(3).tolist())
    
    # Get unique Job IDs from both files
    consolidated_jobs = set(consolidated_data[job_id_columns['consolidated']].unique())
    sales_jobs = set(sales_data[job_id_columns['sales']].unique())
    
    # Find missing jobs (in sales but not in consolidated data)
    missing_jobs = sales_jobs - consolidated_jobs
    
    # Print results
    print(f"\nTotal unique jobs in consolidated data: {len(consolidated_jobs)}")
    print(f"Total unique jobs in sales data: {len(sales_jobs)}")
    
    if missing_jobs:
        print(f"WARNING: {len(missing_jobs)} sales jobs are NOT in the consolidated activity list.")
        print("Missing Job IDs (first few):")
        for job in sorted(list(missing_jobs))[:10]:  # Show first 10 to avoid flooding the console
            print(f"  - {job}")
        if len(missing_jobs) > 10:
            print(f"  ... and {len(missing_jobs) - 10} more")
        is_complete = False
    else:
        print("SUCCESS: All sales jobs are present in the consolidated activity list.")
        is_complete = True
    
    # Create a report of the missing jobs with any available details
    if missing_jobs:
        missing_details = sales_data[sales_data[job_id_columns['sales']].isin(missing_jobs)]
        missing_details.to_csv('missing_sales_jobs.csv', index=False)
        print(f"Details of missing jobs saved to 'missing_sales_jobs.csv'")
    
    return is_complete, list(missing_jobs)