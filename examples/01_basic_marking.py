"""
Example 1: Basic Marking

Demonstrates the simplest way to mark DXF files using shortcuts.
"""

import sys
import os
# Aggiungi la root del progetto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import snapmark as sm

def main():
    folder = "examples/input"
    
    print("=== Example 1A: Mark with filename ===")
    sm.mark_by_name(folder, scale_factor=100)
    
    print("\n=== Example 1B: Mark with first part of filename ===")
    # For files like "PART_123_Q5.dxf", this marks only "PART"
    sm.mark_by_splitted_text(folder, separator='_', part_index=0, scale_factor=50)
    
    print("\n✅ Basic marking completed!")

if __name__ == "__main__":
    main()