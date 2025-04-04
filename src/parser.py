import pandas as pd

def enrich_activity_logs(activity_logs_file, customer_data_file):
    
    # Load data files
    activity_logs = pd.read_csv(activity_logs_file)
    customer_data = pd.read_csv(customer_data_file)

    print(f"Activity logs contains {len(activity_logs)} entries")
    print(f"Customer data contains {len(customer_data)} jobs")
    
    # Identify Job ID column in both files
    job_id_column = None
    
    # Try to find exact 'Job ID' column first
    for df, name in [(activity_logs, "Activity logs"), (customer_data, "Customer data")]:
        for col in df.columns:
            if col.lower() == 'job id':
                if job_id_column is None:
                    job_id_column = col
                elif col != job_id_column:
                    print(f"WARNING: Different Job ID column names found: '{job_id_column}' and '{col}'")
                    print(f"Using '{job_id_column}' for the merge")
                break
    
    # If not found, look for columns with 'job' and 'id'
    if job_id_column is None:
        for df, name in [(activity_logs, "Activity logs"), (customer_data, "Customer data")]:
            possible_cols = [col for col in df.columns if 'job' in col.lower() and 'id' in col.lower()]
            if possible_cols:
                job_id_column = possible_cols[0]
                print(f"Using '{job_id_column}' as the Job ID column")
                break
    
    if job_id_column is None:
        raise ValueError("Could not find Job ID column in either file")
    
    # Ensure Job ID column exists in both files
    if job_id_column not in activity_logs.columns:
        raise ValueError(f"Job ID column '{job_id_column}' not found in activity logs")
    if job_id_column not in customer_data.columns:
        raise ValueError(f"Job ID column '{job_id_column}' not found in customer data")
    
    # Fix all ID columns by removing decimals from numeric values
    id_columns = []
    
    # Identify all potential ID columns in both dataframes
    for df in [activity_logs, customer_data]:
        for col in df.columns:
            if 'id' in col.lower() or '#' in col:
                if col not in id_columns:
                    id_columns.append(col)
    
    print(f"Fixing format for ID columns: {id_columns}")
    
    # Process each ID column in each dataframe
    for df, name in [(activity_logs, "Activity logs"), (customer_data, "Customer data")]:
        for col in id_columns:
            if col in df.columns:
                # Check if the column appears to contain numeric values
                if pd.api.types.is_numeric_dtype(df[col]):
                    # Convert to integers if they're floats with .0
                    if df[col].dropna().apply(lambda x: x == int(x)).all():
                        df[col] = df[col].fillna(-1).astype(int).astype(str)
                        df[col] = df[col].replace('-1', '')
                    else:
                        df[col] = df[col].astype(str).str.strip()
                else:
                    df[col] = df[col].astype(str).str.strip()
    
    # Print sample job IDs for debugging
    print(f"\nSample Job IDs from activity logs: {activity_logs[job_id_column].head(3).tolist()}")
    print(f"Sample Job IDs from customer data: {customer_data[job_id_column].head(3).tolist()}")
    
    # Merge the data
    print(f"\nMerging data on column: '{job_id_column}'")
    enriched_logs = pd.merge(
        activity_logs,
        customer_data,
        on=job_id_column,
        how="left"
    )
    
    # Check for unmatched jobs
    unmatched_count = 0
    customer_id_col = next((col for col in enriched_logs.columns 
                        if 'customer' in col.lower() and 'id' in col.lower()), None)
    
    if customer_id_col:
        unmatched_count = enriched_logs[customer_id_col].isna().sum()
        if unmatched_count > 0:
            print(f"WARNING: {unmatched_count} activity log entries couldn't be matched to a customer.")
            # Print the unmatched Job IDs for investigation
            unmatched_jobs = enriched_logs[enriched_logs[customer_id_col].isna()][job_id_column]
            print(f"First few unmatched Job IDs: {unmatched_jobs.head(5).tolist()}")
            if len(unmatched_jobs) > 5:
                print(f"... and {len(unmatched_jobs) - 5} more")
    
    # Save the detailed enriched data
    enriched_logs.to_csv('detailed_activity_logs.csv', index=False)
    
    # Identify columns that should be consistent for each job
    # This excludes activity-specific columns that can vary within a job
    activity_specific_columns = set(['Action Performed', 'Date', 'Time']) 
    
    # Group by customer, job ID, and action, then count
    customer_id_col = next((col for col in enriched_logs.columns 
                        if 'customer' in col.lower() and 'id' in col.lower()), None)
    customer_name_col = next((col for col in enriched_logs.columns 
                          if 'customer' in col.lower() and 'name' in col.lower()), None)
    
    # Ensure we have the required columns for grouping
    if not customer_id_col:
        print("WARNING: No Customer ID column found for grouping")
        customer_id_col = "Customer ID"  # Use a placeholder
        enriched_logs[customer_id_col] = "Unknown"
    
    if not customer_name_col:
        print("WARNING: No Customer Name column found for grouping")
        customer_name_col = "Customer Name"  # Use a placeholder
        enriched_logs[customer_name_col] = "Unknown"
    
    # Define the grouping columns
    group_by_columns = [customer_name_col, customer_id_col, job_id_column, 'Action Performed']
    
    print(f"\nGrouping by: {group_by_columns}")
    
    # Count actions
    action_counts = enriched_logs.groupby(group_by_columns).size().reset_index(name='Count')
    
    # Get one row per job with all consistent info
    job_columns = [job_id_column]
    job_consistent_columns = [col for col in enriched_logs.columns 
                            if col not in activity_specific_columns 
                            and col not in group_by_columns]
    
    # Merge action counts with job data
    if job_consistent_columns:
        # Get a representative row for each job
        job_data = enriched_logs[group_by_columns[:3] + job_consistent_columns].drop_duplicates(
            subset=group_by_columns[:3])
        
        # Merge with action counts
        consolidated_logs = pd.merge(
            action_counts, 
            job_data, 
            on=group_by_columns[:3], 
            how='left'
        )
    else:
        consolidated_logs = action_counts
    
    # Sort by Customer Name, Job ID, and Count (descending)
    consolidated_logs = consolidated_logs.sort_values(
        [customer_name_col, job_id_column, 'Count'], 
        ascending=[True, True, False]
    )
    
    # Save the consolidated data
    consolidated_logs.to_csv('consolidated_activity_logs.csv', index=False)
    
    print(f"\nEnriched logs shape: {enriched_logs.shape}")
    print(f"Consolidated logs shape: {consolidated_logs.shape}")
    
    return enriched_logs, consolidated_logs