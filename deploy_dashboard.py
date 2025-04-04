#!/usr/bin/env python3
"""
This script deploys the sales report dashboard to a simple HTTP server
for easy access to all reports through a web browser.
"""

import os
import sys
import http.server
import socketserver
import webbrowser
import threading
import time
import socket
import argparse
from pathlib import Path

# First, ensure we've updated the dashboard with all reports
try:
    import update_dashboard
except ImportError:
    print("Warning: update_dashboard.py module not found. Dashboard may not be up to date.")

def check_port_available(port):
    """Check if a port is available to use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def find_available_port(start_port=8000, max_attempts=100):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        if check_port_available(port):
            return port
    raise RuntimeError(f"Could not find an available port after {max_attempts} attempts")

def start_server(directory, port):
    """Start an HTTP server on the specified directory and port."""
    # Change to the specified directory
    os.chdir(directory)
    
    # Create handler and server
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    
    print(f"Server started at http://localhost:{port}")
    print("Press Ctrl+C to stop the server.")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()

def update_and_launch_dashboard(directory=None, port=None, no_browser=False, update=True):
    """Update the dashboard, start server, and open in browser."""
    # Determine base directory
    if directory is None:
        directory = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure the directory exists
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return False
    
    # Update the dashboard if requested
    if update:
        try:
            # Check if update_dashboard.py exists in the directory
            update_script = os.path.join(directory, 'update_dashboard.py')
            if os.path.exists(update_script):
                print("Updating dashboard...")
                # Use importlib to run the update_dashboard module
                import importlib.util
                spec = importlib.util.spec_from_file_location("update_dashboard", update_script)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module.main()
            else:
                print("Warning: update_dashboard.py not found. Skipping dashboard update.")
        except Exception as e:
            print(f"Error updating dashboard: {e}")
            print("Continuing with server launch...")
    
    # Determine port to use
    if port is None:
        port = find_available_port()
    elif not check_port_available(port):
        print(f"Warning: Port {port} is already in use. Finding an available port...")
        port = find_available_port()
    
    # Check if index.html exists
    index_path = os.path.join(directory, 'index.html')
    if not os.path.exists(index_path):
        print(f"Warning: index.html not found at {index_path}")
        print("The server will still run, but you may see a directory listing instead of the dashboard.")
    
    # Start server in a separate thread
    server_thread = threading.Thread(
        target=start_server,
        args=(directory, port),
        daemon=True
    )
    server_thread.start()
    
    # Open the dashboard in a web browser
    url = f"http://localhost:{port}/index.html"
    if not no_browser:
        print(f"Opening dashboard in web browser: {url}")
        # Give the server a moment to start
        time.sleep(1)
        webbrowser.open(url)
    else:
        print(f"Dashboard is available at: {url}")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        return True

def main():
    """Parse command line arguments and run the dashboard server."""
    parser = argparse.ArgumentParser(
        description="Deploy the sales reports dashboard to a local web server."
    )
    parser.add_argument(
        "-d", "--directory", 
        help="Base directory containing the dashboard and reports (default: script directory)"
    )
    parser.add_argument(
        "-p", "--port", 
        type=int, 
        help="Port to use for the HTTP server (default: auto-detect available port)"
    )
    parser.add_argument(
        "--no-browser", 
        action="store_true",
        help="Don't automatically open the dashboard in a web browser"
    )
    parser.add_argument(
        "--no-update", 
        action="store_true",
        help="Don't update the dashboard before launching the server"
    )
    
    args = parser.parse_args()
    
    return update_and_launch_dashboard(
        directory=args.directory,
        port=args.port,
        no_browser=args.no_browser,
        update=not args.no_update
    )

if __name__ == "__main__":
    sys.exit(0 if main() else 1)