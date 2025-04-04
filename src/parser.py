import pandas as pd

def enrich_activity_logs(activity_logs_file, customer_data_file):
    
    activity_logs = pd.read_csv(activity_logs_file)
    customer_data = pd.read_csv(customer_data_file)

    print(f"Activity logs contains {len(activity_logs)} entries")
    print(f"Customer data contains {len(customer_data)} jobs")

    job_id_column = 'Job ID'
    enriched_logs = pd.merge(
        activity_logs,
        customer_data,
        on=job_id_column,
        how="left"
    )

    # Save the detailed enriched data
    enriched_logs.to_csv('detailed_activity_logs.csv', index=False)
    
    # Group by customer, job ID, and action, then count
    group_by_columns = ['Customer Name', 'Customer ID', job_id_column, 'Action Performed']
    
    # Count actions
    action_counts = enriched_logs.groupby(group_by_columns).size().reset_index(name='Count')
    
    # Identify columns that should be consistent for each job
    # This excludes activity-specific columns that can vary within a job
    activity_specific_columns = set(['Action Performed', 'Date', 'Time']) 
    
    # Get one row per job with all consistent info
    job_columns = [job_id_column]
    job_consistent_columns = [col for col in enriched_logs.columns 
                            if col not in activity_specific_columns 
                            and col not in group_by_columns]
    
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
        ['Customer Name', job_id_column, 'Count'], 
        ascending=[True, True, False]
    )
    
    # Save the consolidated data
    consolidated_logs.to_csv('consolidated_activity_logs.csv', index=False)
    
    return enriched_logs, consolidated_logs

    # # Check for unmatched jobs
    # unmatched_count = enriched_logs['Customer Name'].isna().sum()
    # if unmatched_count > 0:
    #     print(f"Warning: {unmatched_count} activity log entries couldn't be matched to a customer.")
    #     # Optional: Print the unmatched Job IDs for investigation
    #     # unmatched_jobs = enriched_logs[enriched_logs['Customer Name'].isna()][job_id_column]
    #     # print("Unmatched Job IDs:", unmatched_jobs.tolist())

    # # Save the detailed enriched data
    # enriched_logs.to_csv('detailed_activity_logs.csv', index=False)
    
    # # Group by customer and action, then count
    # group_by_columns = ['Customer Name', 'Customer ID', 'Action Performed']
    
    # # Count actions
    # action_counts = enriched_logs.groupby(group_by_columns).size().reset_index(name='Count')
    
    # # Get customer-specific columns (should be consistent for each customer)
    # customer_columns = ['Customer Name', 'Customer ID']
    
    # # Find columns that should be consistent for each customer
    # # This excludes activity-specific columns
    # activity_columns = set(['Action Performed', 'Date', 'Time']) 
    # customer_consistent_columns = [col for col in enriched_logs.columns 
    #                               if col not in activity_columns 
    #                               and col not in customer_columns]
    
    # # Get one row per customer with all their consistent info
    # if customer_consistent_columns:
    #     customer_data = enriched_logs[customer_columns + customer_consistent_columns].drop_duplicates(subset=customer_columns)
        
    #     # Merge with action counts
    #     consolidated_logs = pd.merge(action_counts, customer_data, on=customer_columns, how='left')
    # else:
    #     consolidated_logs = action_counts
    
    # # Sort by Customer Name and Count (descending)
    # consolidated_logs = consolidated_logs.sort_values(
    #     ['Customer Name', 'Count'], 
    #     ascending=[True, False]
    # )
    
    # # Save the consolidated data
    # consolidated_logs.to_csv('consolidated_activity_logs.csv', index=False)
    
    # return enriched_logs, consolidated_logs


