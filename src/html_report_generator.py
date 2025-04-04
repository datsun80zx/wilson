import os
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import seaborn as sns
from datetime import datetime

def generate_html_report(conversion_report, output_dir, detailed_data=None, consolidated_data=None):
    """
    Generate an HTML report with charts and tables based on the conversion report data.
    
    Parameters:
    - conversion_report: Dictionary containing the report metrics
    - output_dir: Directory to save the HTML report
    - detailed_data: Optional DataFrame with detailed activity logs
    - consolidated_data: Optional DataFrame with consolidated activity logs
    """
    person = conversion_report.get("person", "Unknown")
    month = conversion_report.get("month", "Unknown")
    report_type = conversion_report.get("report_type", "all")
    
    # Create a filename for the HTML report
    html_filename = f"{person}_month_{month}_{report_type}_report.html"
    html_path = os.path.join(output_dir, html_filename)
    
    # Set up the HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sales Activity Report - {person} - Month {month} - {report_type}</title>
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
            .dashboard {{
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                margin-bottom: 30px;
            }}
            .metric-card {{
                background-color: #f8f9fa;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
                flex: 0 0 calc(33% - 20px);
                text-align: center;
            }}
            .metric-value {{
                font-size: 2em;
                font-weight: bold;
                color: #0066cc;
                margin: 10px 0;
            }}
            .metric-label {{
                font-size: 0.9em;
                color: #666;
            }}
            .chart-container {{
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 30px;
            }}
            .chart-title {{
                font-size: 1.2em;
                margin-bottom: 15px;
                text-align: center;
                color: #444;
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
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Sales Activity & Conversion Report</h1>
            <h2>{person} - Month {month} - {report_type}</h2>
            <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="dashboard">
            <div class="metric-card">
                <div class="metric-label">Total Customers</div>
                <div class="metric-value">{conversion_report.get("total_customers", 0)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Converted Customers</div>
                <div class="metric-value">{conversion_report.get("all_sales_customers", 0)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Conversion Rate</div>
                <div class="metric-value">{conversion_report.get("conversion_rate", 0):.2f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Customers in Both Files</div>
                <div class="metric-value">{conversion_report.get("converted_customers", 0)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Non-Converted Customers</div>
                <div class="metric-value">{conversion_report.get("customers_not_converted", 0)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Sales Only Customers</div>
                <div class="metric-value">{conversion_report.get("sales_only_customers", 0)}</div>
            </div>
        </div>
    """
    
    # Generate conversion funnel chart
    funnel_chart = generate_conversion_funnel(conversion_report)
    if funnel_chart:
        html_content += f"""
        <div class="chart-container">
            <div class="chart-title">Conversion Funnel</div>
            <img src="data:image/png;base64,{funnel_chart}" style="max-width:100%;">
        </div>
        """
    
    # Add activity breakdown chart if consolidated data is available
    if consolidated_data is not None and 'Action Performed' in consolidated_data.columns:
        action_chart = generate_action_breakdown(consolidated_data)
        if action_chart:
            html_content += f"""
            <div class="chart-container">
                <div class="chart-title">Activity Breakdown</div>
                <img src="data:image/png;base64,{action_chart}" style="max-width:100%;">
            </div>
            """
    
    # Add sample of detailed data if available
    if detailed_data is not None:
        html_content += """
        <h2>Sample Activity Data</h2>
        <table>
            <tr>
        """
        
        # Add headers
        sample_columns = min(10, len(detailed_data.columns))  # Limit to 10 columns
        for column in detailed_data.columns[:sample_columns]:
            html_content += f"<th>{column}</th>"
        
        html_content += "</tr>"
        
        # Add rows (limit to 10 rows for preview)
        sample_rows = min(10, len(detailed_data))
        for i in range(sample_rows):
            html_content += "<tr>"
            for column in detailed_data.columns[:sample_columns]:
                value = detailed_data.iloc[i][column]
                html_content += f"<td>{value}</td>"
            html_content += "</tr>"
        
        html_content += """
        </table>
        """
    
    # Add footer
    html_content += """
        <div class="footer">
            <p>This report was automatically generated by the Sales Activity Analysis System.</p>
        </div>
    </body>
    </html>
    """
    
    # Write the HTML to a file
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML report generated: {html_path}")
    return html_path

def generate_conversion_funnel(report_data):
    """
    Generate a conversion funnel chart based on the report data.
    """
    try:
        # Set seaborn style
        sns.set_style("whitegrid")
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Data for the funnel
        stages = ['Total Customers', 'Converted Customers']
        values = [
            report_data.get("total_customers", 0),
            report_data.get("all_sales_customers", 0)
        ]
        
        # Create horizontal bar chart for funnel
        colors = ['#3498db', '#2ecc71']
        bars = plt.barh(stages, values, color=colors, height=0.5)
        
        # Add data labels
        for bar in bars:
            width = bar.get_width()
            label_x_pos = width if width < max(values) * 0.3 else width * 0.9
            label_color = 'black' if width < max(values) * 0.3 else 'white'
            plt.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{int(width)}',
                    va='center', color=label_color)
        
        # Add conversion rate annotation
        conversion_rate = report_data.get("conversion_rate", 0)
        plt.annotate(f'Conversion Rate: {conversion_rate:.2f}%',
                    xy=(0.5, 0.1), xycoords='figure fraction',
                    bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3),
                    ha='center')
        
        # Set title and labels
        plt.title('Conversion Funnel', fontsize=16, pad=20)
        plt.xlabel('Number of Customers')
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert plot to base64 encoded image
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return image_base64
    except Exception as e:
        print(f"Error generating conversion funnel chart: {e}")
        return None

def generate_action_breakdown(consolidated_data):
    """
    Generate a chart showing the breakdown of actions performed.
    """
    try:
        if 'Action Performed' not in consolidated_data.columns or 'Count' not in consolidated_data.columns:
            return None
        
        # Aggregate data by action
        action_counts = consolidated_data.groupby('Action Performed')['Count'].sum().reset_index()
        action_counts = action_counts.sort_values('Count', ascending=False)
        
        # Limit to top 10 actions for readability
        if len(action_counts) > 10:
            action_counts = action_counts.head(10)
            chart_title = 'Top 10 Actions Performed'
        else:
            chart_title = 'Actions Performed'
        
        # Set seaborn style
        sns.set_style("whitegrid")
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Create bar chart
        bars = plt.bar(action_counts['Action Performed'], action_counts['Count'], 
                     color=sns.color_palette("viridis", len(action_counts)))
        
        # Add data labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', rotation=0)
        
        # Set title and labels
        plt.title(chart_title, fontsize=16, pad=20)
        plt.xlabel('Action Type')
        plt.ylabel('Count')
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert plot to base64 encoded image
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return image_base64
    except Exception as e:
        print(f"Error generating action breakdown chart: {e}")
        return None