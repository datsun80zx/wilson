import os
import glob

def setup_paths():
    """
    Set up and return a dictionary of file paths used throughout the application.
    This centralizes path configuration and makes it easier to change locations.
    """
    # Base project directory (can be adjusted as needed)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Define subdirectories
    raw_input_dir = os.path.join(base_dir, "raw_inputs")
    converted_input_dir = os.path.join(base_dir, "converted_inputs")
    output_dir = os.path.join(base_dir, "outputs")  # Output to project root, adjust if needed
    
    # Initialize path structure
    paths = {
        "base_dir": base_dir,
        "raw_input_dir": raw_input_dir,
        "converted_input_dir": converted_input_dir,
        "output_dir": output_dir,
        "people": {}  # This will store paths for each person
    }
    
    return paths

def scan_input_files(paths):
    """
    Scan the raw input directory to identify files for each person and month.
    Also identifies shared job report files.
    """
    raw_input_dir = paths["raw_input_dir"]
    
    # Find all Excel files
    excel_files = glob.glob(os.path.join(raw_input_dir, "*.xlsx"))
    excel_files.extend(glob.glob(os.path.join(raw_input_dir, "*.xls")))
    
    # Track master job reports by month
    master_job_reports = {}
    
    # First pass: identify master job reports
    for excel_path in excel_files:
        filename = os.path.basename(excel_path)
        parts = os.path.splitext(filename)[0].split('_')
        
        # Check if this is a total_jobs file
        if len(parts) >= 2 and parts[0] == "total" and "job" in parts[1]:
            month = parts[-1]
            master_job_reports[month] = excel_path
            print(f"Found master job report for month {month}: {filename}")
    
    # Second pass: identify per-person files
    for excel_path in excel_files:
        filename = os.path.basename(excel_path)
        
        # Skip the master job reports in this pass
        if os.path.basename(excel_path).startswith("total_jobs"):
            continue
        
        # Split the filename and remove extension
        parts = os.path.splitext(filename)[0].split('_')
        
        if len(parts) >= 2:  # Need at least person and month
            person = parts[0]  # First part is person
            month = parts[-1]  # Last part is month
            
            # The data type is everything in between, joined back with underscores
            data_type = '_'.join(parts[1:-1]) if len(parts) > 2 else "unknown"
            
            # Create nested structure in paths dictionary
            if person not in paths["people"]:
                paths["people"][person] = {"months": {}}
            
            if month not in paths["people"][person]["months"]:
                # Create person-specific subdirectories in converted_inputs and outputs
                person_month_converted_dir = os.path.join(paths["converted_input_dir"], person, f"month_{month}")
                person_month_output_dir = os.path.join(paths["output_dir"], person, f"month_{month}")
                
                # Create directories
                os.makedirs(person_month_converted_dir, exist_ok=True)
                os.makedirs(person_month_output_dir, exist_ok=True)
                
                paths["people"][person]["months"][month] = {
                    "raw_files": {},
                    "converted_dir": person_month_converted_dir,
                    "converted_files": {},
                    "output_dir": person_month_output_dir,
                    "output_files": {}
                }
            
            # Store the raw input file path
            paths["people"][person]["months"][month]["raw_files"][data_type] = excel_path
            
            # Add reference to the master job report if available for this month
            if month in master_job_reports:
                paths["people"][person]["months"][month]["raw_files"]["jobs_report"] = master_job_reports[month]
            
            # Define output file paths
            output_files = paths["people"][person]["months"][month]["output_files"]
            output_dir = paths["people"][person]["months"][month]["output_dir"]
            
            # Define standard output files
            output_files["consolidated"] = os.path.join(output_dir, f"consolidated_activity_logs.csv")
            output_files["detailed"] = os.path.join(output_dir, f"detailed_activity_logs.csv")
            output_files["sales_report"] = os.path.join(output_dir, f"sales_conversion_report.csv")
            output_files["converted"] = os.path.join(output_dir, f"converted_customers.csv")
            output_files["non_converted"] = os.path.join(output_dir, f"non_converted_customers.csv")
            output_files["missing_jobs"] = os.path.join(output_dir, f"missing_sales_jobs.csv")
    
    return paths

def find_required_files(input_files):
    """
    Find the required files for processing based on partial name matches.
    """
    file_mapping = {
        "sales_activity": None,
        "jobs_report": None,
        "commission_isr": None
    }
    
    # Find matching files based on partial name matches
    for data_type, file_path in input_files.items():
        if "activity" in data_type:
            file_mapping["sales_activity"] = file_path
        elif "job" in data_type or "jobs" in data_type:
            file_mapping["jobs_report"] = file_path
        elif "sales" in data_type:
            file_mapping["commission_isr"] = file_path
    
    return file_mapping

