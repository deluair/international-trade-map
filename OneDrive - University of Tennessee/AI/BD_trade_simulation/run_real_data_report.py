#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run Real Data Report

This script generates an HTML report based on real Bangladesh trade data.
"""

import os
import sys
import webbrowser
from generate_html_report import create_html_report

def main():
    """Main entry point for the script"""
    print("Generating Bangladesh Trade Analysis Report using real data")
    
    # Create HTML report (no results_file provided will prioritize real data)
    report_file = create_html_report()
    
    # Try to open the report in a web browser
    print("Attempting to open the report in your web browser...")
    try:
        webbrowser.open('file://' + os.path.abspath(report_file))
    except Exception as e:
        print(f"Error opening report in browser: {e}")
        print(f"Please open the report manually: {report_file}")

if __name__ == "__main__":
    main() 