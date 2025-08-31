#!/usr/bin/env python3
"""
Simple test to read the GEDCOM file
"""

def test_read():
    print("Testing file reading...")
    try:
        with open("Arbre 31_08_2025.ged", 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"Successfully read {len(lines)} lines")
            print("About to print first 10 lines...")

            for i in range(min(10, len(lines))):
                line = lines[i]
                print(f"Line {i}: '{line.strip()}'")
                if '|' in line:
                    print(f"  -> Contains | separator")
                else:
                    print(f"  -> No | separator")

            print("Test completed successfully")

    except Exception as e:
        print(f"Error reading file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_read()
