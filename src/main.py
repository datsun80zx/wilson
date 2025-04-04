import os
from parser import enrich_activity_logs
from excel_to_csv import convert_excel_to_csv
from sales_validator import validate_sales_in_activity
from report_generator import generate_sales_conversion_report, generate_consolidated_reports
from file_manager import find_required_files, setup_paths, scan_input_files

# def process_data_for_person_month(person, month, paths):
#     """
#     Process data for a specific person and month.
#     """
#     print(f"Processing data for {person} - Month {month}")
    
#     # Get the paths for this person/month
#     month_data = paths["people"][person]["months"][month]
#     input_files = month_data["converted_files"]
#     output_files = month_data["output_files"]
    
#     # Find required files
#     file_mapping = find_required_files(input_files)
    
#     # Check if we have all required files
#     missing_types = [key for key, value in file_mapping.items() if value is None]
#     if missing_types:
#         print(f"WARNING: Missing required files for {person}/Month {month}: {missing_types}")
#         return False
    
#     # Step 1: Enrich and consolidate the activity logs
#     print(f"  Enriching activity logs...")
#     enriched_logs, consolidated_logs = enrich_activity_logs(
#         file_mapping["sales_activity"], 
#         file_mapping["jobs_report"]
#     )
    
#     # Important: The consolidated_logs now exists in memory but might not yet be fully 
#     # written to disk. We should use the in-memory version for validation.
    
#     # Step 2: Validate if all sales jobs are in the consolidated logs
#     print(f"  Validating sales jobs...")
#     is_complete, missing_jobs = validate_sales_in_activity(
#         consolidated_logs,  # Pass the DataFrame directly instead of the file path
#         file_mapping["commission_isr"]
#     )
    
#     # Step 3: Generate sales conversion report
#     print(f"  Generating sales conversion report...")
#     conversion_report = generate_sales_conversion_report(
#         consolidated_logs,  # Pass the DataFrame directly instead of the file path
#         file_mapping["commission_isr"]
#     )
    
#     print(f"Data processing complete for {person} - Month {month}")
#     return True

def process_data_for_person_month(person, month, paths):
    """
    Process data for a specific person and month.
    """
    print(f"Processing data for {person} - Month {month}")
    
    # Get the paths for this person/month
    month_data = paths["people"][person]["months"][month]
    converted_files = month_data["converted_files"]
    output_dir = month_data["output_dir"]
    
    # Find required files
    file_mapping = find_required_files(converted_files)
    
    # Check if we have all required files
    missing_types = [key for key, value in file_mapping.items() if value is None]
    if missing_types:
        print(f"WARNING: Missing required files for {person}/Month {month}: {missing_types}")
        return None
    
    # Step 1: Enrich and consolidate the activity logs
    print(f"  Enriching activity logs...")
    enriched_logs, consolidated_logs = enrich_activity_logs(
        file_mapping["sales_activity"], 
        file_mapping["jobs_report"]
    )
    
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
        month
    )
    
    print(f"Data processing complete for {person} - Month {month}")
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
    
    # Process data for each person and month
    print("\nBeginning data processing...")
    for person, person_data in paths["people"].items():
        for month in person_data["months"].keys():
            report = process_data_for_person_month(person, month, paths)
            if report:  # If processing was successful
                all_reports.append(report)
    
    # Generate consolidated reports
    if all_reports:
        print("\nGenerating consolidated reports...")
        generate_consolidated_reports(all_reports, paths["output_dir"])
    
    print("\nAll data processing complete!")

if __name__ == "__main__":
    main()