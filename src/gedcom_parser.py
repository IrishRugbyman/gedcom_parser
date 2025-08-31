#!/usr/bin/env python3
"""
GEDCOM Parser for Family Tree Analysis
Converts GEDCOM format to structured JSON for LLM querying
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sys


class GEDCOMParser:
    def __init__(self, gedcom_file: str):
        self.gedcom_file = gedcom_file
        self.individuals = {}
        self.families = {}
        self.lines = []

    def parse(self) -> Dict:
        """Parse the GEDCOM file and return structured data"""
        print("=== Starting GEDCOM parsing ===")
        try:
            print("Reading GEDCOM file...")
            try:
                self._read_file()
            except Exception as read_error:
                print(f"Error in _read_file(): {read_error}")
                import traceback
                traceback.print_exc()
                self.lines = []  # Set empty lines to continue
            print(f"Processing {len(self.lines)} lines...")

            print("Extracting individuals...")
            try:
                self._extract_individuals()
            except Exception as ind_error:
                print(f"Error in _extract_individuals(): {ind_error}")
                import traceback
                traceback.print_exc()
            print(f"Found {len(self.individuals)} individuals")

            print("Extracting families...")
            self._extract_families()
            print(f"Found {len(self.families)} families")

            print("Resolving relationships...")
            self._resolve_relationships()
            print("=== Parsing completed successfully ===")
        except Exception as e:
            print(f"Error in parse(): {e}")
            import traceback
            traceback.print_exc()
            # Try to continue with empty data
            return {
                "individuals": {},
                "families": {},
                "summary": {
                    "total_individuals": 0,
                    "total_families": 0,
                    "parsed_at": datetime.now().isoformat(),
                    "error": str(e)
                }
            }

        return {
            "individuals": self.individuals,
            "families": self.families,
            "summary": {
                "total_individuals": len(self.individuals),
                "total_families": len(self.families),
                "parsed_at": datetime.now().isoformat()
            }
        }

    def _read_file(self):
        """Read the GEDCOM file"""
        print(f"Reading file: {self.gedcom_file}")
        with open(self.gedcom_file, 'r', encoding='utf-8') as f:
            raw_lines = f.readlines()
            print(f"Read {len(raw_lines)} raw lines")
            # Just strip whitespace, no | separators in this file
            self.lines = [line.strip() for line in raw_lines if line.strip()]
            print(f"After filtering: {len(self.lines)} clean lines")

    def _extract_individuals(self):
        """Extract individual records from GEDCOM"""
        print("=== INDIVIDUAL EXTRACTION STARTING ===")
        print(f"About to process {len(self.lines)} lines")

        # Simple test to see if INDI records exist
        indi_count = sum(1 for line in self.lines if 'INDI' in line)
        print(f"Found {indi_count} lines containing 'INDI'")

        try:
            current_individual = None
            current_record = {}
            current_section = None
            individual_count = 0

            processed_lines = 0
            for line_num, line in enumerate(self.lines):
                processed_lines += 1
                line = line.strip()
                if not line:
                    continue

                # Debug: Show first few lines
                if line_num < 5:
                    print(f"Processing line {line_num}: '{line}'")

                # Parse GEDCOM line format: level tag [value]
                parts = line.split(' ', 2)
                if len(parts) < 2:
                    continue

                try:
                    level = int(parts[0])
                    tag = parts[1] if len(parts) > 1 else ""
                    value = parts[2] if len(parts) > 2 else ""
                except ValueError as e:
                    continue

                # Debug: Show condition check for first few lines
                if line_num < 20 and len(parts) >= 3:
                    condition = level == 0 and len(parts) >= 3 and parts[2] == 'INDI'
                    print(f"INDI condition check: level={level}, parts[2]='{parts[2]}', condition={condition}")

                # Start of new individual record
                if level == 0 and len(parts) >= 3 and parts[2] == 'INDI':
                    print(f"Found individual: {tag} (line {line_num})")
                    # Save previous individual
                    if current_individual and current_record:
                        self.individuals[current_individual] = current_record
                        individual_count += 1

                    # Start new individual
                    current_individual = tag.replace('@', '').replace('I', '').replace('@', '')
                    print(f"Processing individual ID: {current_individual}")
                    current_record = {
                        'id': current_individual,
                        'name': '',
                        'gender': '',
                        'birth': {},
                        'death': {},
                        'occupation': '',
                        'notes': [],
                        'families_as_child': [],
                        'families_as_spouse': [],
                        'media': []
                    }
                    current_section = None

                # Individual data
                elif current_individual and level == 1:
                    if tag == 'NAME':
                        # Clean up GEDCOM name format: "Firstname /SURNAME/" -> "Firstname SURNAME"
                        if value:
                            # Remove surrounding slashes and clean up internal slashes
                            cleaned_name = value.strip('/')
                            # Handle cases like "Charles /LAMBOLEZ" -> "Charles LAMBOLEZ"
                            if '/' in cleaned_name:
                                parts = [part.strip() for part in cleaned_name.split('/') if part.strip()]
                                current_record['name'] = ' '.join(parts)
                            else:
                                current_record['name'] = cleaned_name
                        else:
                            current_record['name'] = ''
                    elif tag == 'SEX':
                        current_record['gender'] = value if value else ''
                    elif tag == 'OCCU':
                        current_record['occupation'] = value if value else ''
                    elif tag == 'BIRT':
                        current_section = 'birth'
                    elif tag == 'DEAT':
                        current_section = 'death'
                    elif tag == 'FAMC':
                        fam_id = value.replace('@', '').replace('F', '') if value else ''
                        if fam_id:
                            current_record['families_as_child'].append(fam_id)
                    elif tag == 'FAMS':
                        fam_id = value.replace('@', '').replace('F', '') if value else ''
                        if fam_id:
                            current_record['families_as_spouse'].append(fam_id)
                    elif tag == 'OBJE':
                        current_section = 'media'
                    elif tag == 'NOTE':
                        current_section = 'notes'
                        if value:
                            current_record['notes'].append(value)

                # Sub-level data (birth, death, media, notes)
                elif current_individual and level == 2 and current_section:
                    if current_section in ['birth', 'death']:
                        if tag == 'DATE':
                            current_record[current_section]['date'] = value if value else ''
                        elif tag == 'PLAC':
                            current_record[current_section]['place'] = value if value else ''
                    elif current_section == 'media':
                        if tag == 'FILE':
                            current_record['media'].append(value if value else '')
                    elif current_section == 'notes':
                        if tag in ['CONT', 'CONC']:
                            if value:
                                current_record['notes'].append(value)
                        elif tag == 'NOTE':
                            if value:
                                current_record['notes'].append(value)

            # Save last individual
            if current_individual and current_record:
                self.individuals[current_individual] = current_record
                individual_count += 1

            print(f"Finished extracting {individual_count} individuals")
            print(f"Total lines processed: {processed_lines}")
        except Exception as e:
            print(f"Error in _extract_individuals: {e}")
            import traceback
            traceback.print_exc()

    def _extract_families(self):
        """Extract family records from GEDCOM"""
        print("Starting family extraction...")
        current_family = None
        current_record = {}
        family_count = 0

        for line_num, line in enumerate(self.lines):
            line = line.strip()
            if not line:
                continue

            parts = line.split(' ', 2)
            if len(parts) < 2:
                continue

            try:
                level = int(parts[0])
                tag = parts[1] if len(parts) > 1 else ""
                value = parts[2] if len(parts) > 2 else ""
            except ValueError as e:
                print(f"Error parsing family line {line_num}: '{line}' - {e}")
                continue

            # Start of new family record
            if level == 0 and len(parts) >= 3 and parts[2] == 'FAM':
                print(f"Found family: {tag}")
                # Save previous family
                if current_family and current_record:
                    self.families[current_family] = current_record
                    family_count += 1

                # Start new family
                current_family = tag.replace('@', '').replace('F', '').replace('@', '')
                current_record = {
                    'id': current_family,
                    'marriage': {},
                    'husband': '',
                    'wife': '',
                    'children': [],
                    'notes': [],
                    'divorced': False
                }

            # Family data
            elif current_family and level == 1:
                if tag == 'MARR':
                    pass  # Marriage section
                elif tag == 'DIV':
                    current_record['divorced'] = True
                elif tag == 'SEP':
                    current_record['divorced'] = True
                elif tag == 'HUSB':
                    current_record['husband'] = value.replace('@', '').replace('I', '') if value else ''
                elif tag == 'WIFE':
                    current_record['wife'] = value.replace('@', '').replace('I', '') if value else ''
                elif tag == 'CHIL':
                    child_id = value.replace('@', '').replace('I', '') if value else ''
                    if child_id:
                        current_record['children'].append(child_id)
                elif tag == 'NOTE':
                    if value:
                        current_record['notes'].append(value)

            # Marriage details
            elif current_family and level == 2:
                if tag == 'DATE':
                    current_record['marriage']['date'] = value if value else ''
                elif tag == 'PLAC':
                    current_record['marriage']['place'] = value if value else ''

        # Save last family
        if current_family and current_record:
            self.families[current_family] = current_record
            family_count += 1

        print(f"Finished extracting {family_count} families")

    def _resolve_relationships(self):
        """Resolve family relationships and add computed fields"""
        # Add family relationships to individuals
        for ind_id, individual in self.individuals.items():
            individual['parents'] = []
            individual['spouse'] = []
            individual['children'] = []

            # Find parents from families_as_child
            for fam_id in individual['families_as_child']:
                if fam_id in self.families:
                    family = self.families[fam_id]
                    if family['husband']:
                        individual['parents'].append(family['husband'])
                    if family['wife']:
                        individual['parents'].append(family['wife'])

            # Find spouse and children from families_as_spouse
            for fam_id in individual['families_as_spouse']:
                if fam_id in self.families:
                    family = self.families[fam_id]
                    # Add spouse
                    if family['husband'] == ind_id and family['wife']:
                        individual['spouse'].append(family['wife'])
                    elif family['wife'] == ind_id and family['husband']:
                        individual['spouse'].append(family['husband'])
                    # Add children
                    individual['children'].extend(family['children'])

        # Clean up empty lists
        for ind_id, individual in self.individuals.items():
            individual['parents'] = [p for p in individual['parents'] if p]
            individual['spouse'] = [s for s in individual['spouse'] if s]
            individual['children'] = [c for c in individual['children'] if c]


class GenealogyQueryEngine:
    """Query engine for genealogy data"""

    def __init__(self, data: Dict):
        self.data = data
        self.individuals = data['individuals']
        self.families = data['families']

    def find_person(self, name_query: str) -> List[Dict]:
        """Find individuals by name"""
        results = []
        query = name_query.lower()

        for ind_id, person in self.individuals.items():
            if query in person['name'].lower():
                results.append(person)

        return results

    def get_person_details(self, person_id: str) -> Optional[Dict]:
        """Get detailed information about a person"""
        if person_id not in self.individuals:
            return None

        person = self.individuals[person_id].copy()

        # Resolve parent names
        person['parent_names'] = []
        for parent_id in person['parents']:
            if parent_id in self.individuals:
                person['parent_names'].append(self.individuals[parent_id]['name'])

        # Resolve spouse names
        person['spouse_names'] = []
        for spouse_id in person['spouse']:
            if spouse_id in self.individuals:
                person['spouse_names'].append(self.individuals[spouse_id]['name'])

        # Resolve children names
        person['children_names'] = []
        for child_id in person['children']:
            if child_id in self.individuals:
                person['children_names'].append(self.individuals[child_id]['name'])

        return person

    def get_family_tree(self, person_id: str, generations: int = 3) -> Dict:
        """Get family tree for a person"""
        if person_id not in self.individuals:
            return {}

        def build_tree(pid: str, gen: int, max_gen: int) -> Dict:
            if gen >= max_gen or pid not in self.individuals:
                return {}

            person = self.individuals[pid]
            tree = {
                'id': pid,
                'name': person['name'],
                'birth': person['birth'],
                'death': person['death'],
                'generation': gen
            }

            if gen < max_gen - 1:
                tree['parents'] = []
                for parent_id in person['parents']:
                    parent_tree = build_tree(parent_id, gen + 1, max_gen)
                    if parent_tree:
                        tree['parents'].append(parent_tree)

                tree['children'] = []
                for child_id in person['children']:
                    child_tree = build_tree(child_id, gen - 1, max_gen)
                    if child_tree:
                        tree['children'].append(child_tree)

            return tree

        return build_tree(person_id, 0, generations)

    def search_by_location(self, location: str) -> List[Dict]:
        """Find people by birth/death location"""
        results = []
        query = location.lower()

        for ind_id, person in self.individuals.items():
            birth_place = person['birth'].get('place', '').lower()
            death_place = person['death'].get('place', '').lower()

            if query in birth_place or query in death_place:
                results.append(person)

        return results

    def get_statistics(self) -> Dict:
        """Get genealogy statistics"""
        stats = {
            'total_individuals': len(self.individuals),
            'total_families': len(self.families),
            'gender_distribution': {'M': 0, 'F': 0, 'Unknown': 0},
            'occupation_distribution': {},
            'century_distribution': {},
            'living_people': 0
        }

        for person in self.individuals.values():
            # Gender stats
            gender = person.get('gender', 'Unknown')
            if gender in stats['gender_distribution']:
                stats['gender_distribution'][gender] += 1
            else:
                stats['gender_distribution']['Unknown'] += 1

            # Occupation stats
            occ = person.get('occupation', '')
            if occ:
                stats['occupation_distribution'][occ] = stats['occupation_distribution'].get(occ, 0) + 1

            # Birth century
            birth_date = person['birth'].get('date', '')
            if birth_date and len(birth_date) >= 4:
                try:
                    year = int(birth_date[-4:])
                    century = (year // 100) + 1
                    stats['century_distribution'][f"{century}th century"] = stats['century_distribution'].get(f"{century}th century", 0) + 1
                except ValueError:
                    pass

            # Living people (no death date)
            if not person['death'].get('date'):
                stats['living_people'] += 1

        return stats


def main():
    if len(sys.argv) < 2:
        # Use default file if none provided
        gedcom_file = "data/Arbre 31_08_2025.ged"
        print(f"No file provided, using default: {gedcom_file}")
    else:
        gedcom_file = sys.argv[1]

    # Parse GEDCOM
    parser = GEDCOMParser(gedcom_file)
    data = parser.parse()

    # Save to JSON
    if gedcom_file.startswith("data/"):
        output_file = gedcom_file.replace('.ged', '_parsed.json')
    else:
        output_file = f"data/{gedcom_file.split('/')[-1].replace('.ged', '_parsed.json')}"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Parsed data saved to {output_file}")

    # Create query engine and show some examples
    query_engine = GenealogyQueryEngine(data)

    print("\n=== Genealogy Statistics ===")
    stats = query_engine.get_statistics()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")

    print("\n=== Sample Queries ===")
    print("You can now query your family tree data!")

    # Example: Find Quentin (mentioned in the notes)
    quentin_results = query_engine.find_person("Quentin")
    if quentin_results:
        print(f"\nFound Quentin: {quentin_results[0]['name']}")
        details = query_engine.get_person_details(quentin_results[0]['id'])
        if details:
            print(f"Birth: {details['birth']}")
            print(f"Parents: {', '.join(details['parent_names'])}")


if __name__ == "__main__":
    main()
