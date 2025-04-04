import os
import glob
import pandas as pd

def convert_excel_to_csv(paths, delimiter=',', quotechar='"', encoding='utf-8'):
    """
    Convert all Excel files to CSV while maintaining the person/month/report_type structure.
    """
    for person, person_data in paths["people"].items():
        for month, month_data in person_data["months"].items():
            for report_type, report_data in month_data["report_types"].items():
                print(f"Converting files for {person} - Month {month} - Report Type: {report_type}")
                
                converted_dir = report_data["converted_dir"]
                
                # Convert each raw file for this person/month/report_type
                for data_type, excel_path in report_data["raw_files"].items():
                    # Create CSV filename
                    filename = os.path.basename(excel_path)
                    file_base = os.path.splitext(filename)[0]
                    csv_path = os.path.join(converted_dir, file_base + ".csv")
                    
                    print(f"  Converting {filename} to CSV...")
                    
                    # Read the Excel file
                    df = pd.read_excel(excel_path)
                    
                    # Save as CSV with specified parameters
                    df.to_csv(csv_path, index=False, sep=delimiter, quotechar=quotechar, encoding=encoding)
                    
                    # Store the CSV path
                    report_data["converted_files"][data_type] = csv_path
    
    return paths