"""
Example 4: Advanced Pipeline

Demonstrates complex workflows with IterationManager.
"""
import snapmark as sm

def main():
    folder = "examples/input"
    
    # Build custom sequence
    seq = (sm.SequenceBuilder()
           .file_name()
           .folder(num_chars=2)
           .build())
    
    print("=== Pipeline: Align + Mark + Count ===")
    
    # Create pipeline manager
    manager = sm.IterationManager(folder, use_backup_system=True)
    
    # Add multiple operations
    manager.add_operation(
        sm.Aligner(),  # Align drawing
        sm.AddMark(seq, scale_factor=100, align='c'),  # Add marking
        sm.CountHoles(sm.find_circle_by_radius(min_diam=5, max_diam=10))  # Count holes
    )
    
    # Execute all operations
    stats = manager.execute()
    
    print(f"\n✅ Pipeline completed!")
    print(f"   Processed: {stats['processed']} files")
    print(f"   Modified: {stats['modified']} files")
    
    # Example with single file
    print("\n=== Pipeline on Single File ===")
    
    sm.process_single_file(
        "examples/input/F1.dxf",
        sm.Aligner(),
        sm.AddMark(seq, scale_factor=100),
        sm.AddX(sm.find_circle_by_radius(5, 10), x_size=5),
        use_backup=True
    )
    
    print("\n✅ Single file pipeline completed!")

if __name__ == "__main__":
    main()