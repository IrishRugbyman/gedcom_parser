# Genealogy Analysis Tool Documentation

## Overview

This tool provides functionality for parsing GEDCOM (GEnealogical Data COMmunication) files and analyzing genealogical data. GEDCOM is a specification for exchanging genealogical data between different genealogy software.

## Features

### GEDCOM Parser
The `GEDCOMParser` class is responsible for:
- Reading GEDCOM files
- Extracting individual records
- Extracting family records
- Resolving relationships between individuals

### Query Engine
The `GenealogyQueryEngine` class provides methods for:
- Searching individuals by name
- Getting detailed information about a person
- Building family trees
- Searching by location
- Generating statistics

## Data Structure

### Individuals
Each individual record contains:
- `id`: Unique identifier
- `name`: Full name
- `gender`: Gender (M/F)
- `birth`: Birth information (date and place)
- `death`: Death information (date and place)
- `occupation`: Occupation
- `notes`: Additional notes
- `families_as_child`: List of family IDs where this person is a child
- `families_as_spouse`: List of family IDs where this person is a spouse
- `media`: List of media files
- `parents`: List of parent IDs (computed)
- `spouse`: List of spouse IDs (computed)
- `children`: List of children IDs (computed)

### Families
Each family record contains:
- `id`: Unique identifier
- `marriage`: Marriage information (date and place)
- `husband`: Husband's ID
- `wife`: Wife's ID
- `children`: List of children IDs
- `notes`: Additional notes
- `divorced`: Divorce status

## Usage Examples

### Parsing a GEDCOM File
```python
from gedcom_parser import GEDCOMParser

parser = GEDCOMParser("data/sample.ged")
data = parser.parse()
```

### Querying Data
```python
from gedcom_parser import GenealogyQueryEngine

query_engine = GenealogyQueryEngine(data)

# Find people by name
results = query_engine.find_person("John")

# Get detailed information
details = query_engine.get_person_details("I1")

# Get family tree
tree = query_engine.get_family_tree("I1", generations=3)

# Search by location
people = query_engine.search_by_location("Paris")
```

## GEDCOM Format

GEDCOM files use a hierarchical structure with levels:
- Level 0: Record markers (INDI for individuals, FAM for families)
- Level 1: Top-level record data (NAME, SEX, BIRT, DEAT, etc.)
- Level 2: Sub-data (DATE, PLAC, etc.)

Example:
```
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 BIRT
2 DATE 01 JAN 1980
2 PLAC New York, NY
```

## Error Handling

The parser includes error handling for:
- File reading errors
- Malformed GEDCOM data
- Missing records
- Invalid references

If errors occur during parsing, they will be printed to the console, and the parser will attempt to continue with available data.