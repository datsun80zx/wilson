import os
from parser import enrich_activity_logs
from excel_to_csv import convert_excel_to_csv
from sales_validator import validate_sales_in_activity
from report_generator import generate_sales_conversion_report, generate_consolidated_reports
from file_manager import find_required_files, setup_paths, scan_input_files
from html_report_generator import generate_html_report  # Import the new module
from datetime import datetime

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
        report_type
    )
    
    # Step 4: Generate HTML report
    print(f"  Generating HTML report...")
    html_report_path = generate_html_report(
        conversion_report,
        output_dir,
        enriched_logs,  # Pass detailed data
        consolidated_logs  # Pass consolidated data
    )
    
    print(f"Data processing complete for {person} - Month {month} - Report Type: {report_type}")
    print(f"HTML Report available at: {html_report_path}")
    
    return conversion_report

def generate_master_html_report(all_reports, monthly_reports, person_reports, base_output_dir):
    """
    Generate a master HTML report with overview of all data.
    """
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Master Sales Activity Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid #ddd;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #0066cc;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
                margin-top: 30px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 30px;
            }}
            th, td {{
                padding: 10px;
                border: 1px solid #ddd;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .footer {{
                text-align: center;
                font-size: 0.8em;
                color: #888;
                margin-top: 40px;
                border-top: 1px solid #ddd;
                padding-top: 10px;
            }}
            .report-link {{
                display: block;
                margin: 5px 0;
                color: #0066cc;
                text-decoration: none;
            }}
            .report-link:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Master Sales Activity & Conversion Report</h1>
            <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <h2>Monthly Performance</h2>
        <table>
            <tr>
                <th>Month</th>
                <th>Report Type</th>
                <th>Total Customers</th>
                <th>Converted Customers</th>
                <th>Conversion Rate</th>
            </tr>
    """
    
    # Add monthly data
    for _, row in monthly_reports.iterrows():
        html_content += f"""
            <tr>
                <td>{row['month']}</td>
                <td>{row['report_type']}</td>
                <td>{row['total_customers']}</td>
                <td>{row['all_sales_customers']}</td>
                <td>{row['conversion_rate']}%</td>
            </tr>
        """
    
    html_content += """
        </table>
        
        <h2>Performance by Person</h2>
        <table>
            <tr>
                <th>Person</th>
                <th>Report Type</th>
                <th>Total Customers</th>
                <th>Converted Customers</th>
                <th>Conversion Rate</th>
            </tr>
    """
    
    # Add person data
    for _, row in person_reports.iterrows():
        html_content += f"""
            <tr>
                <td>{row['person']}</td>
                <td>{row['report_type']}</td>
                <td>{row['total_customers']}</td>
                <td>{row['all_sales_customers']}</td>
                <td>{row['conversion_rate']}%</td>
            </tr>
        """
    
    html_content += """
        </table>
        
        <h2>All Reports</h2>
        <table>
            <tr>
                <th>Person</th>
                <th>Month</th>
                <th>Report Type</th>
                <th>Total Customers</th>
                <th>Converted Customers</th>
                <th>Conversion Rate</th>
            </tr>
    """
    
    # Add all report data
    for _, row in all_reports.iterrows():
        html_content += f"""
            <tr>
                <td>{row['person']}</td>
                <td>{row['month']}</td>
                <td>{row['report_type']}</td>
                <td>{row['total_customers']}</td>
                <td>{row['all_sales_customers']}</td>
                <td>{row['conversion_rate']}%</td>
            </tr>
        """
    
    html_content += """
        </table>
        
        <h2>Report Links</h2>
        <div class="report-links">
    """
    
    # Add links to individual reports
    for person in sorted(set(all_reports['person'])):
        html_content += f"<h3>{person}</h3>"
        person_data = all_reports[all_reports['person'] == person]
        
        for _, row in person_data.iterrows():
            report_file = f"{row['person']}_month_{row['month']}_{row['report_type']}_report.html"
            report_path = os.path.join("../", row['person'], f"month_{row['month']}", row['report_type'], report_file)
            html_content += f"""
                <a class="report-link" href="{report_path}">
                    Month {row['month']} - {row['report_type']} Report
                </a>
            """
    
    # Add footer
    html_content += """
        </div>
        
        <div class="footer">
            <p>This report was automatically generated by the Sales Activity Analysis System.</p>
        </div>
    </body>
    </html>
    """
    
    # Write the HTML to a file
    html_path = os.path.join(base_output_dir, "master_report.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nMaster HTML report generated: {html_path}")
    return html_path

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
        all_reports_df, monthly_reports, person_reports = generate_consolidated_reports(all_reports, paths["output_dir"])
        
        # Generate master HTML report
        print("\nGenerating master HTML report...")
        master_html_path = generate_master_html_report(
            all_reports_df, 
            monthly_reports, 
            person_reports, 
            paths["output_dir"]
        )
    
    print("\nAll data processing complete!")

if __name__ == "__main__":
    main()