"""
Example 2: Custom Sequences

Shows how to build custom marking sequences using SequenceBuilder.
"""

import sys
from pathlib import Path
from datetime import datetime   

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


import snapmark as sm

def main():
    file_1 = "input/nested/BB.dxf"
    file_2 = "input/nested/1412DP_P1_S235JR_SP4_Q1.DXF"
    
    # Example 1: Filename + first 2 chars of folder
    print("=== Custom Sequence 1: File + Folder ===")
    seq1 = (sm.SequenceBuilder()
            .file_name()
            .folder(num_chars=2, level=1)
            .folder(num_chars=2)
            .build())
    
    sm.mark_with_sequence(file_1, seq1, excluded_layers=["MARCATURA"])
    
    # Example 2: First part of filename only
    print("\n=== Custom Sequence 2: First Part Only ===")
    today = datetime.now().strftime("%Y-%m-%d")

    seq2 = (sm.SequenceBuilder()
            .file_part(separator='_', part_index=0)
            .literal(today)
            .build())
    
    sm.mark_with_sequence(file_2, seq2, scale_factor=100)
    
    print("\n✅ Custom sequences completed!")

if __name__ == "__main__":
    main()