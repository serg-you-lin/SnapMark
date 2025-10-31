"""
Example 3: Counting Holes

Demonstrates hole counting with and without multipliers.
"""
import snapmark as sm
import re

def main():
    folder = "examples/input_multiple"
    
    # Example 1: Simple counting
    print("=== Example 1: Simple Count ===")
    stats = sm.quick_count_holes(folder, min_diam=5, max_diam=13, verbose=True)
    print(f"\n📊 Total holes: {stats['total_count']}")
    
    # Example 2: With multiplier (extract quantity from filename)
    print("\n=== Example 2: Count with Multiplier ===")
    
    def extract_quantity(filename):
        """
        Extracts quantity from filename.
        Example: PART_Q5.dxf → returns 5
        """
        match = re.search(r'Q(\d+)', filename, re.IGNORECASE)
        return int(match.group(1)) if match else 1
    
    mult_stats = sm.quick_count_holes(
        folder, 
        min_diam=5, 
        max_diam=13,
        multiplier=extract_quantity,
        verbose=True
    )
    print(f"\n📊 Total holes (with multiplier): {mult_stats['total_count']}")
    
    print("\n✅ Counting completed!")

if __name__ == "__main__":
    main()