#!/usr/bin/env python3
"""
GEDCOM Genealogy Parser - Main Script
Convert GEDCOM files to structured JSON for LLM querying
"""

import sys
import os
import argparse
import json

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from gedcom_parser import GEDCOMParser, GenealogyQueryEngine


def main():
    """Main function to run the GEDCOM parser"""

    parser = argparse.ArgumentParser(
        description="GEDCOM Genealogy Parser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Parse default GEDCOM file
  python main.py data/my_family.ged        # Parse specific file
  python main.py --search "John Doe"       # Search for a person
  python main.py --stats-only              # Show only statistics
        """
    )

    parser.add_argument(
        'gedcom_file',
        nargs='?',
        default='data/Arbre 31_08_2025.ged',
        help='Path to GEDCOM file (default: data/Arbre 31_08_2025.ged)'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output JSON file path (default: <input>_parsed.json)'
    )

    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Show statistics only, do not save JSON'
    )

    parser.add_argument(
        '--search',
        help='Search for a person by name'
    )

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.gedcom_file):
        print(f"❌ Error: GEDCOM file '{args.gedcom_file}' not found!")
        print("\n💡 Tip: Place your .ged file in the 'data/' directory")
        sys.exit(1)

    try:
        print(f"🚀 Parsing: {args.gedcom_file}")

        # Parse GEDCOM file
        gedcom_parser = GEDCOMParser(args.gedcom_file)
        data = gedcom_parser.parse()

        # Show statistics
        query_engine = GenealogyQueryEngine(data)
        stats = query_engine.get_statistics()

        print(f"\n📊 Statistics:")
        print(f"   👥 Individuals: {stats['total_individuals']}")
        print(f"   👨‍👩‍👧‍👦 Families: {stats['total_families']}")
        print(f"   ❤️ Living: {stats['living_people']}")

        # Search functionality
        if args.search:
            print(f"\n🔍 Searching for '{args.search}':")
            results = query_engine.find_person(args.search)

            if results:
                for i, person in enumerate(results[:10], 1):
                    print(f"   {i}. {person['name']} (ID: {person['id']})")
                    if person.get('birth', {}).get('date'):
                        print(f"      Born: {person['birth']['date']}")
                if len(results) > 10:
                    print(f"   ... and {len(results) - 10} more")
            else:
                print("   No results found")

        # Save JSON output
        if not args.stats_only:
            output_file = args.output or args.gedcom_file.replace('.ged', '_parsed.json')
            print(f"\n💾 Saving to: {output_file}")

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            size_mb = os.path.getsize(output_file) / (1024*1024)
            print(f"   📏 Size: {size_mb:.1f} MB")
        print("\n✅ Success! Ready for LLM queries")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
