from parser import enrich_activity_logs
from sales_validator import validate_sales_in_activity
from report_generator import generate_sales_conversion_report

def main():
    activity_logs_file = "/home/richard/workspace/github.com/datsun80zx/wilson_data_project/inputs/sales_activity.csv"
    customer_data_file = "/home/richard/workspace/github.com/datsun80zx/wilson_data_project/inputs/jobs_report.csv"
    consolidated_file = "/home/richard/workspace/github.com/datsun80zx/wilson_data_project/consolidated_activity_logs.csv"  # The file we just created
    sales_file = "/home/richard/workspace/github.com/datsun80zx/wilson_data_project/inputs/commission_isr.csv"  # Your file with sales Job IDs

    # Step 1: Enrich and consolidate the activity logs
    enriched_logs, consolidated_logs = enrich_activity_logs(activity_logs_file, customer_data_file)
    
    # Step 2: Validate if all sales jobs are in the consolidated logs
    is_complete, missing_jobs = validate_sales_in_activity(consolidated_file, sales_file)
    
    # Step 3: Generate sales conversion report
    conversion_report = generate_sales_conversion_report(consolidated_file, sales_file)
    
    print("\nData processing pipeline complete!")

    # enriched_logs, consolidated_logs = enrich_activity_logs(activity_logs_file, customer_data_file)
    
    # print("Data processing complete!")
    # print(f"Detailed data saved to 'detailed_activity_logs.csv'")
    # print(f"Consolidated data saved to 'consolidated_activity_logs.csv'")

    
    
    # is_complete, missing_jobs = validate_sales_in_activity(consolidated_file, sales_file)

    # print(missing_jobs)
    # print(is_complete)
if __name__ == "__main__":
    main()