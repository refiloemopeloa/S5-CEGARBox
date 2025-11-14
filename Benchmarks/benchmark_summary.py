import re
import csv
import argparse
import os
import sys

def load_formulas(formula_file):
    """Load formulas from formulas_generated.txt and return as list"""
    formulas = []
    try:
        with open(formula_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    formulas.append(line)
        print(f"Loaded {len(formulas)} formulas from {formula_file}")
        return formulas
    except FileNotFoundError:
        print(f"Error: Formula file {formula_file} not found")
        return None
    except Exception as e:
        print(f"Error reading formula file {formula_file}: {e}")
        return None

def parse_cegar_file(filename, formulas):
    """Parse CEGAR benchmark file and extract required attributes"""
    results = []
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Split by formula sections (assuming each formula starts with "FORMULA:")
    formula_sections = content.split('FORMULA:')
    
    for i, section in enumerate(formula_sections[1:], 1):  # Start from index 1
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        # Use formula from formulas_generated.txt based on index
        if i - 1 < len(formulas):  # i-1 because we started enumeration from 1
            formula = formulas[i - 1]
        else:
            print(f"Warning: Index {i-1} out of range for formulas list")
            continue
        
        # Initialize variables
        satisfiable = None
        time = None
        
        # Parse each line in the section
        for line in lines:
            line = line.strip()
            
            # Check for SATISFIABLE/UNSATISFIABLE
            if 'SATISFIABLE' in line.upper() and 'UNSATISFIABLE' not in line.upper():
                satisfiable = 'SATISFIABLE'
            elif 'UNSATISFIABLE' in line.upper():
                satisfiable = 'UNSATISFIABLE'
            
            # Check for TOTAL TIME
            if 'TOTAL TIME' in line.upper():
                # Extract time value (could be in seconds, ms, etc.)
                time_match = re.search(r'([\d.]+)', line, re.IGNORECASE)
                if time_match:
                    time = time_match.group(1)
                    # convert to seconds
                    time = str(float(time) / 1000)
        
        # Only add if we found all required information
        if formula and satisfiable is not None and time is not None:
            results.append({
                'formula': formula,
                'satisfiable': satisfiable,
                'time': time,
                'solver': 'CEGAR'
            })
    
    return results

def parse_lcks5_file(filename, formulas):
    """Parse LCKS5 benchmark file and extract required attributes"""
    results = []
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Split by formula sections (assuming each formula starts with "FORMULA:")
    formula_sections = content.split('FORMULA:')
    
    for i, section in enumerate(formula_sections[1:], 1):  # Start from index 1
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        # Use formula from formulas_generated.txt based on index
        if i - 1 < len(formulas):  # i-1 because we started enumeration from 1
            formula = formulas[i - 1]
        else:
            print(f"Warning: Index {i-1} out of range for formulas list")
            continue
        
        # Initialize variables
        satisfiable = None
        time = None
        
        # Parse each line in the section
        for line in lines:
            line = line.strip()
            
            # Check for SATISFIABLE/UNSATISFIABLE
            if 'SATISFIABLE' in line.upper() and 'UNSATISFIABLE' not in line.upper():
                satisfiable = 'SATISFIABLE'
            elif 'UNSATISFIABLE' in line.upper():
                satisfiable = 'UNSATISFIABLE'
            
            # Check for TOTAL TIME
            if 'TOTAL TIME' in line.upper():
                # Extract time value (could be in seconds, ms, etc.)
                time_match = re.search(r'([\d.]+)', line, re.IGNORECASE)
                if time_match:
                    time = time_match.group(1)
                    # convert to seconds
                    time = str(float(time))
        
        # Only add if we found all required information
        if formula and satisfiable is not None and time is not None:
            results.append({
                'formula': formula,
                'satisfiable': satisfiable,
                'time': time,
                'solver': 'LCKS5'
            })
    
    return results

def parse_s52sat_file(filename, formulas):
    """Parse S52SAT benchmark file and extract required attributes"""
    results = []
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Split by formula sections
    formula_sections = content.split('FORMULA:')
    
    for i, section in enumerate(formula_sections[1:], 1):  # Skip first empty section
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        # Use formula from formulas_generated.txt based on index
        if i - 1 < len(formulas):  # i-1 because we started enumeration from 1
            formula = formulas[i - 1]
        else:
            print(f"Warning: Index {i-1} out of range for formulas list")
            continue
        
        # Initialize variables
        satisfiable = None
        time = None
        
        # Parse each line in the section
        for line in lines:
            line = line.strip()
            
            # Check for SATISFIABLE/UNSATISFIABLE
            if 'SATISFIABLE' in line.upper() and 'UNSATISFIABLE' not in line.upper():
                satisfiable = 'SATISFIABLE'
            elif 'UNSATISFIABLE' in line.upper():
                satisfiable = 'UNSATISFIABLE'
            
            # Check for TOTAL TIME (or just TIME)
            if 'TOTAL TIME' in line.upper():
                # Extract time value
                time_match = re.search(r'([\d.]+)', line, re.IGNORECASE)
                if time_match:
                    time = time_match.group(1)
                    # If time is in ms, convert to seconds
                    time = str(float(time) / 1000)
        
        # Only add if we found all required information
        if formula and satisfiable is not None and time is not None:
            results.append({
                'formula': formula,
                'satisfiable': satisfiable,
                'time': time,
                'solver': 'S52SAT'
            })
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Parse benchmark files and extract results to CSV')
    parser.add_argument('--formulas', '-f', type=str, help='Path to formulas_generated.txt', default='formulas_generated.txt')
    parser.add_argument('--cegar', '-c', type=str, help='Path to CEGAR benchmark file', default='CEGAR/benchmark_CEGAR.txt')
    parser.add_argument('--lcks5', '-l', type=str, help='Path to LCKS5 benchmark file', default='LCKS5/benchmark_LCKS5.txt')
    parser.add_argument('--s52sat', '-s', type=str, help='Path to S52SAT benchmark file', default='S52SAT/benchmark_S52SAT_nbModals.txt')
    parser.add_argument('--output', '-o', type=str, help='Output CSV file path', default='results_summary.csv')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
        # Load formulas first
    formulas = load_formulas(args.formulas)
    if formulas is None:
        sys.exit(1)
        
    all_results = []
    files_processed = 0
    
    # Parse each benchmark file
    file_configs = [
        (args.cegar, parse_cegar_file, 'CEGAR'),
        (args.lcks5, parse_lcks5_file, 'LCKS5'),
        (args.s52sat, parse_s52sat_file, 'S52SAT')
    ]
    
    for file_path, parser_func, solver_name in file_configs:
        if os.path.exists(file_path):
            try:
                if args.verbose:
                    print(f"Parsing {solver_name} benchmark: {file_path}")
                results = parser_func(file_path, formulas)
                all_results.extend(results)
                if args.verbose:
                    print(f"Found {len(results)} results from {solver_name}")
                files_processed += 1
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        else:
            print(f"Warning: File not found: {file_path}")
    
    # Write results to CSV
    if all_results:
        try:
            with open(args.output, 'w', newline='') as csvfile:
                fieldnames = ['formula', 'satisfiable', 'time', 'solver']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for result in all_results:
                    writer.writerow(result)
            
            print(f"\nSuccessfully processed {files_processed} files")
            print(f"Wrote {len(all_results)} results to {args.output}")
        except Exception as e:
            print(f"Error writing to {args.output}: {e}")
            sys.exit(1)
    else:
        print("No results found to write to CSV")
        sys.exit(1)

if __name__ == "__main__":
    main()