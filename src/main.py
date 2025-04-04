import os
from parser import enrich_activity_logs
from excel_to_csv import convert_excel_to_csv
from sales_validator import validate_sales_in_activity
from report_generator import generate_sales_conversion_report, generate_consolidated_reports
from file_manager import find_required_files, setup_paths, scan_input_files

def process_data_for_person_month_report_type(person, month, report_type, paths):
    """
    Process data for a specific person, month, and report type.
    """
    print(f"Processing data for {person} - Month {month} - Report Type: {report_type}")
    
    # Get the paths for this person/month/report_type
    report_data = paths["people"][person]["months"][month]["report_types"][report_type]
    converted_files = report_data["converted_files"]
    output_dir = report_data["output_dir"]
    
    # Find required files
    file_mapping = find_required_files(converted_files)
    
    # Check if we have all required files
    missing_types = [key for key, value in file_mapping.items() if value is None]
    if missing_types:
        print(f"WARNING: Missing required files for {person}/Month {month}/Report Type {report_type}: {missing_types}")
        return None
    
    # Step 1: Enrich and consolidate the activity logs
    print(f"  Enriching activity logs...")
    enriched_logs, consolidated_logs = enrich_activity_logs(
        file_mapping["sales_activity"], 
        file_mapping["jobs_report"]
    )
    
    # Debug info
    print("\nDEBUG: Checking for potential data issues...")
    print(f"Enriched logs shape: {enriched_logs.shape}")
    print(f"Consolidated logs shape: {consolidated_logs.shape}")

    # Sample the first few rows to verify the merge worked correctly
    print("\nSample from enriched logs (first 3 rows):")
    print(enriched_logs.head(3))

    print("\nSample from consolidated logs (first 3 rows):")
    print(consolidated_logs.head(3))

    # Check for null values in key columns
    job_id_col = next((col for col in consolidated_logs.columns if 'job' in col.lower() and 'id' in col.lower()), None)
    if job_id_col:
        null_job_ids = consolidated_logs[job_id_col].isnull().sum()
        print(f"\nNull values in {job_id_col}: {null_job_ids}")

    customer_id_col = next((col for col in consolidated_logs.columns if 'customer' in col.lower() and 'id' in col.lower()), None)
    if customer_id_col:
        null_customer_ids = consolidated_logs[customer_id_col].isnull().sum()
        print(f"Null values in {customer_id_col}: {null_customer_ids}")
        
    # Step 2: Validate if all sales jobs are in the consolidated logs
    print(f"  Validating sales jobs...")
    is_complete, missing_jobs = validate_sales_in_activity(
        consolidated_logs,  # Pass the DataFrame directly instead of the file path
        file_mapping["commission_isr"]
    )
    
    # Step 3: Generate sales conversion report
    print(f"  Generating sales conversion report...")
    conversion_report = generate_sales_conversion_report(
        consolidated_logs,  # Pass the DataFrame directly instead of the file path
        file_mapping["commission_isr"],
        output_dir,
        person,
        month,
        report_type  # Add report_type to the function parameters
    )
    
    print(f"Data processing complete for {person} - Month {month} - Report Type: {report_type}")
    return conversion_report

def main():
    print("Starting data processing pipeline...")
    
    # Initialize paths
    paths = setup_paths()
    
    # Scan raw input directory for files
    print("Scanning input files...")
    paths = scan_input_files(paths)
    
    # Check if we found any files
    if not any(paths["people"]):
        print("No input files found. Please check the raw_inputs directory.")
        return
    
    # Convert Excel files to CSV
    print("Converting Excel files to CSV...")
    paths = convert_excel_to_csv(paths)
    
    # Store reports for later consolidation
    all_reports = []
    
    # Process data for each person, month, and report type
    print("\nBeginning data processing...")
    for person, person_data in paths["people"].items():
        for month, month_data in person_data["months"].items():
            for report_type in month_data["report_types"].keys():
                report = process_data_for_person_month_report_type(person, month, report_type, paths)
                if report:  # If processing was successful
                    all_reports.append(report)
    
    # Generate consolidated reports
    if all_reports:
        print("\nGenerating consolidated reports...")
        generate_consolidated_reports(all_reports, paths["output_dir"])
    
    print("\nAll data processing complete!")

if __name__ == "__main__":
    main()