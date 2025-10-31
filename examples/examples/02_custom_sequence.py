"""
Example 2: Custom Sequences

Shows how to build custom marking sequences using SequenceBuilder.
"""
import snapmark as sm

def main():
    folder = "examples/input_customizable"
    
    # Example 1: Filename + first 2 chars of folder
    print("=== Custom Sequence 1: File + Folder ===")
    seq1 = (sm.SequenceBuilder()
            .file_name()
            .folder(num_chars=2)
            .build())
    
    sm.mark_with_sequence(folder, seq1, scale_factor=100)
    
    # Example 2: First part of filename only
    print("\n=== Custom Sequence 2: First Part Only ===")
    seq2 = (sm.SequenceBuilder()
            .file_part(separator='_', part_index=0)
            .build())
    
    sm.mark_with_sequence(folder, seq2, scale_factor=100)
    
    print("\n✅ Custom sequences completed!")

if __name__ == "__main__":
    main()