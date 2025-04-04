#!/usr/bin/env python3
"""
Script to automatically update the index.html dashboard with links to all available reports.
This script scans the output directory structure and generates an up-to-date dashboard.
"""

import os
import re
import glob
from datetime import datetime
from bs4 import BeautifulSoup

def find_all_reports(base_dir):
    """
    Scan the output directory to find all report files.
    
    Returns a dictionary of reports organized by person, month, and report_type.
    """
    all_reports = {
        'master': [],
        'consolidated': [],
        'people': {}
    }
    
    # Find master reports
    master_html = os.path.join(base_dir, 'outputs', 'master_report.html')
    if os.path.exists(master_html):
        all_reports['master'].append({
            'path': master_html,
            'type': 'html',
            'title': 'Master Report',
            'description': 'Complete overview of all sales data'
        })
    
    # Find consolidated CSV reports
    consolidated_csvs = glob.glob(os.path.join(base_dir, 'outputs', '*_report.csv'))
    for csv_path in consolidated_csvs:
        report_name = os.path.basename(csv_path)
        report_type = 'monthly' if 'monthly' in report_name else 'person' if 'person' in report_name else 'consolidated'
        
        title = 'Monthly Report' if report_type == 'monthly' else 'Personnel Report' if report_type == 'person' else 'Consolidated Report'
        
        all_reports['consolidated'].append({
            'path': csv_path,
            'type': 'csv',
            'report_type': report_type,
            'title': title,
            'description': f'{title} showing all {report_type} data'
        })
    
    # Find per-person reports
    person_dirs = glob.glob(os.path.join(base_dir, 'outputs', '*'))
    for person_dir in person_dirs:
        if not os.path.isdir(person_dir):
            continue
        
        person_name = os.path.basename(person_dir)
        if person_name not in all_reports['people']:
            all_reports['people'][person_name] = {'months': {}}
        
        # Find month directories
        month_dirs = glob.glob(os.path.join(person_dir, 'month_*'))
        for month_dir in month_dirs:
            month = os.path.basename(month_dir).replace('month_', '')
            
            if month not in all_reports['people'][person_name]['months']:
                all_reports['people'][person_name]['months'][month] = {'report_types': {}}
            
            # Find report type directories
            report_type_dirs = glob.glob(os.path.join(month_dir, '*'))
            for report_type_dir in report_type_dirs:
                if not os.path.isdir(report_type_dir):
                    continue
                
                report_type = os.path.basename(report_type_dir)
                
                if report_type not in all_reports['people'][person_name]['months'][month]['report_types']:
                    all_reports['people'][person_name]['months'][month]['report_types'][report_type] = []
                
                # Find HTML reports
                html_reports = glob.glob(os.path.join(report_type_dir, '*.html'))
                for html_path in html_reports:
                    report_name = os.path.basename(html_path)
                    
                    all_reports['people'][person_name]['months'][month]['report_types'][report_type].append({
                        'path': html_path,
                        'type': 'html',
                        'report_name': report_name,
                        'title': f'{person_name} - Month {month} - {report_type} Report',
                        'description': f'Detailed report for {person_name} for month {month} ({report_type})'
                    })
                
                # Find CSV reports
                csv_reports = glob.glob(os.path.join(report_type_dir, '*.csv'))
                for csv_path in csv_reports:
                    report_name = os.path.basename(csv_path)
                    report_label = report_name.replace(f"{person_name}_month_{month}_{report_type}_", "").replace(".csv", "")
                    report_label = report_label.replace("_", " ").title()
                    
                    all_reports['people'][person_name]['months'][month]['report_types'][report_type].append({
                        'path': csv_path,
                        'type': 'csv',
                        'report_name': report_name,
                        'report_label': report_label,
                        'title': f'{person_name} - {report_label} ({month})',
                        'description': f'{report_label} for {person_name} for month {month} ({report_type})'
                    })
    
    return all_reports

def generate_dashboard_html(base_dir, all_reports):
    """
    Generate an updated index.html dashboard with links to all reports.
    """
    # Read the template
    template_path = os.path.join(base_dir, 'index.html')
    if not os.path.exists(template_path):
        # Create a basic template if it doesn't exist
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sales Analysis Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px 0;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5rem;
        }
        .header p {
            margin: 10px 0 0;
            font-size: 1.2rem;
            opacity: 0.8;
        }
        .card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 25px;
            margin-bottom: 30px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .card h2 {
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }
        .card p {
            color: #7f8c8d;
        }
        .button {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background-color 0.3s ease;
            margin-top: 10px;
        }
        .button:hover {
            background-color: #2980b9;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            grid-gap: 20px;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #7f8c8d;
            font-size: 0.9rem;
            margin-top: 40px;
            border-top: 1px solid #ecf0f1;
        }
        .tag {
            display: inline-block;
            background-color: #e3f2fd;
            color: #1565c0;
            border-radius: 4px;
            padding: 5px 10px;
            font-size: 0.8rem;
            margin-right: 8px;
            margin-bottom: 8px;
        }
        .last-updated {
            font-size: 0.8rem;
            color: #95a5a6;
            margin-top: 15px;
            font-style: italic;
        }
        .report-section {
            margin-bottom: 30px;
        }
        .report-section h2 {
            color: #2c3e50;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Sales Activity Analysis Dashboard</h1>
        <p>Comprehensive view of sales performance and customer activities</p>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>Overview</h2>
            <p>This dashboard provides access to all sales activity reports, including conversion rates, customer activities, and detailed analytics.</p>
        </div>
        
        <h2>Reports</h2>
        <div id="reports-container" class="dashboard-grid">
            <!-- Dynamic reports will be inserted here -->
        </div>
        
        <div class="footer">
            <p>Sales Activity Analysis System &copy; 2025</p>
            <p>For support or questions, please contact the IT department.</p>
            <p class="last-updated">Last updated: <span class="date"></span></p>
        </div>
    </div>
    
    <script>
        // Update all date elements with current date
        document.addEventListener('DOMContentLoaded', function() {
            const today = new Date();
            const dateString = today.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            
            const dateElements = document.querySelectorAll('.date');
            dateElements.forEach(function(element) {
                element.textContent = dateString;
            });
        });
    </script>
</body>
</html>""")
    
    # Load the template
    with open(template_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # Find or create the reports container
    reports_container = soup.find(id='reports-container')
    if not reports_container:
        reports_container = soup.new_tag('div')
        reports_container['id'] = 'reports-container'
        reports_container['class'] = 'dashboard-grid'
        soup.body.find('div', class_='container').append(reports_container)
    
    # Clear existing content
    reports_container.clear()
    
    # Add Master Report card if available
    if all_reports['master']:
        master_card = soup.new_tag('div')
        master_card['class'] = 'card'
        
        master_title = soup.new_tag('h2')
        master_title.string = 'Master Report'
        master_card.append(master_title)
        
        master_desc = soup.new_tag('p')
        master_desc.string = 'Complete overview of all sales and activity data across all personnel and time periods.'
        master_card.append(master_desc)
        
        tags_div = soup.new_tag('div')
        
        tag = soup.new_tag('span')
        tag['class'] = 'tag'
        tag.string = 'Complete'
        tags_div.append(tag)
        
        tag = soup.new_tag('span')
        tag['class'] = 'tag'
        tag.string = 'Overview'
        tags_div.append(tag)
        
        master_card.append(tags_div)
        
        master_link = soup.new_tag('a')
        master_link['href'] = os.path.relpath(all_reports['master'][0]['path'], base_dir)
        master_link['class'] = 'button'
        master_link.string = 'View Master Report'
        master_card.append(master_link)
        
        updated_div = soup.new_tag('div')
        updated_div['class'] = 'last-updated'
        updated_text = 'Last updated: '
        updated_span = soup.new_tag('span')
        updated_span['class'] = 'date'
        updated_div.append(updated_text)
        updated_div.append(updated_span)
        
        master_card.append(updated_div)
        reports_container.append(master_card)
    
    # Add Consolidated Report cards
    for report in all_reports['consolidated']:
        report_card = soup.new_tag('div')
        report_card['class'] = 'card'
        
        report_title = soup.new_tag('h2')
        report_title.string = report['title']
        report_card.append(report_title)
        
        report_desc = soup.new_tag('p')
        report_desc.string = report['description']
        report_card.append(report_desc)
        
        tags_div = soup.new_tag('div')
        
        tag = soup.new_tag('span')
        tag['class'] = 'tag'
        tag.string = report['report_type'].capitalize()
        tags_div.append(tag)
        
        tag = soup.new_tag('span')
        tag['class'] = 'tag'
        tag.string = 'CSV'
        tags_div.append(tag)
        
        report_card.append(tags_div)
        
        report_link = soup.new_tag('a')
        report_link['href'] = os.path.relpath(report['path'], base_dir)
        report_link['class'] = 'button'
        report_link.string = f'View {report["title"]}'
        report_card.append(report_link)
        
        updated_div = soup.new_tag('div')
        updated_div['class'] = 'last-updated'
        updated_text = 'Last updated: '
        updated_span = soup.new_tag('span')
        updated_span['class'] = 'date'
        updated_div.append(updated_text)
        updated_div.append(updated_span)
        
        report_card.append(updated_div)
        reports_container.append(report_card)
    
    # Add Per-Person Report cards
    for person, person_data in all_reports['people'].items():
        for month, month_data in person_data['months'].items():
            for report_type, reports in month_data['report_types'].items():
                # Find HTML report if available
                html_reports = [r for r in reports if r['type'] == 'html']
                
                if html_reports:
                    report = html_reports[0]  # Use the first HTML report
                    
                    report_card = soup.new_tag('div')
                    report_card['class'] = 'card'
                    
                    report_title = soup.new_tag('h2')
                    report_title.string = f'{person.capitalize()} - {month.capitalize()} - {report_type.upper()}'
                    report_card.append(report_title)
                    
                    report_desc = soup.new_tag('p')
                    report_desc.string = report['description']
                    report_card.append(report_desc)
                    
                    tags_div = soup.new_tag('div')
                    
                    tag = soup.new_tag('span')
                    tag['class'] = 'tag'
                    tag.string = person.capitalize()
                    tags_div.append(tag)
                    
                    tag = soup.new_tag('span')
                    tag['class'] = 'tag'
                    tag.string = f'Month {month}'
                    tags_div.append(tag)
                    
                    tag = soup.new_tag('span')
                    tag['class'] = 'tag'
                    tag.string = report_type.upper()
                    tags_div.append(tag)
                    
                    report_card.append(tags_div)
                    
                    report_link = soup.new_tag('a')
                    report_link['href'] = os.path.relpath(report['path'], base_dir)
                    report_link['class'] = 'button'
                    report_link.string = 'View Report'
                    report_card.append(report_link)
                    
                    updated_div = soup.new_tag('div')
                    updated_div['class'] = 'last-updated'
                    updated_text = 'Last updated: '
                    updated_span = soup.new_tag('span')
                    updated_span['class'] = 'date'
                    updated_div.append(updated_text)
                    updated_div.append(updated_span)
                    
                    report_card.append(updated_div)
                    reports_container.append(report_card)
    
    # Add "Run Pipeline" card
    pipeline_card = soup.new_tag('div')
    pipeline_card['class'] = 'card'
    
    pipeline_title = soup.new_tag('h2')
    pipeline_title.string = 'Generate New Reports'
    pipeline_card.append(pipeline_title)
    
    pipeline_desc = soup.new_tag('p')
    pipeline_desc.string = 'Run the data processing pipeline to generate fresh reports with new data.'
    pipeline_card.append(pipeline_desc)
    
    tags_div = soup.new_tag('div')
    
    tag = soup.new_tag('span')
    tag['class'] = 'tag'
    tag.string = 'Processing'
    tags_div.append(tag)
    
    tag = soup.new_tag('span')
    tag['class'] = 'tag'
    tag.string = 'Update'
    tags_div.append(tag)
    
    pipeline_card.append(tags_div)
    
    pipeline_link = soup.new_tag('a')
    pipeline_link['href'] = '#'
    pipeline_link['onclick'] = "alert('To generate new reports, run the main.sh script from the command line.'); return false;"
    pipeline_link['class'] = 'button'
    pipeline_link.string = 'Run Pipeline'
    pipeline_card.append(pipeline_link)
    
    reports_container.append(pipeline_card)
    
    # Update the date in the script section
    date_script = soup.find('script')
    if date_script and 'Date' in date_script.text:
        # Script exists and contains date functionality, no need to modify
        pass
    else:
        # Add or update the date script
        if date_script:
            date_script.extract()
        
        new_script = soup.new_tag('script')
        new_script.string = """
        // Update all date elements with current date
        document.addEventListener('DOMContentLoaded', function() {
            const today = new Date();
            const dateString = today.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            
            const dateElements = document.querySelectorAll('.date');
            dateElements.forEach(function(element) {
                element.textContent = dateString;
            });
        });
        """
        soup.body.append(new_script)
    
    # Write the updated HTML
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print(f"Dashboard updated at {template_path}")
    return template_path

def main():
    """
    Main function to scan directories and update the dashboard.
    """
    # Determine the base directory (script location)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Scanning directories in {base_dir}...")
    all_reports = find_all_reports(base_dir)
    
    # Count reports found
    total_reports = len(all_reports['master']) + len(all_reports['consolidated'])
    for person, person_data in all_reports['people'].items():
        for month, month_data in person_data['months'].items():
            for report_type, reports in month_data['report_types'].items():
                total_reports += len(reports)
    
    print(f"Found {total_reports} reports in total.")
    
    # Generate the updated dashboard
    dashboard_path = generate_dashboard_html(base_dir, all_reports)
    print(f"Dashboard updated successfully at: {dashboard_path}")
    print("Open this file in a web browser to access all reports.")

if __name__ == "__main__":
    main()