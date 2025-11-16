#!/usr/bin/env python3
"""
Benchmark Summary Generator
Processes benchmark files from CEGAR, S52SAT, and LCKS5 solvers and generates a CSV summary.
"""

import argparse
import csv
import re
from typing import List, Dict, Optional


def parse_cegar_file(filepath: str) -> List[Dict[str, str]]:
    """Parse CEGAR benchmark file."""
    results = []
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split by FORMULA: entries
    entries = re.split(r'FORMULA:\s*', content)[1:]  # Skip first empty split
    
    for entry in entries:
        lines = entry.strip().split('\n')
        if not lines:
            continue
            
        formula = lines[0].strip()
        
        # Check for timeout
        if 'Timeout' in entry:
            total_time_match = re.search(r'TOTAL TIME:\s*([\d.]+)', entry)
            if total_time_match:
                total_time = float(total_time_match.group(1)) * 1000  # Convert seconds to ms
                results.append({
                    'formula': formula,
                    'satisfiable': 'TIMEOUT',
                    'solve_time': 'TIMEOUT',
                    'total_time': f'{total_time:.6f}',
                    'solver': 'CEGAR'
                })
            continue
        
        # Check if invalid (no Solved marker)
        if 'Solved' not in entry:
            continue
        
        # Extract satisfiability
        satisfiable = 'Unsatisfiable' if 'Unsatisfiable' in entry else 'Satisfiable'
        
        # Extract times
        solve_time_match = re.search(r'SOLVE TIME:\s*([\d.]+)', entry)
        total_time_match = re.search(r'TOTAL TIME:\s*([\d.]+)', entry)
        
        if solve_time_match and total_time_match:
            results.append({
                'formula': formula,
                'satisfiable': satisfiable,
                'solve_time': solve_time_match.group(1),
                'total_time': total_time_match.group(1),
                'solver': 'CEGAR'
            })
    
    return results


def parse_s52sat_file(filepath: str) -> List[Dict[str, str]]:
    """Parse S52SAT benchmark file."""
    results = []
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split by FORMULA: entries
    entries = re.split(r'FORMULA:\s*', content)[1:]  # Skip first empty split
    
    for entry in entries:
        lines = entry.strip().split('\n')
        if not lines:
            continue
            
        formula = lines[0].strip()
        
        # Check for timeout
        if 'Timeout' in entry:
            results.append({
                'formula': formula,
                'satisfiable': 'TIMEOUT',
                'solve_time': 'TIMEOUT',
                'total_time': '300000.0',  # 5 minutes in ms
                'solver': 'S52SAT'
            })
            continue
        
        # Check if invalid (no time information)
        if 'Total time(ms):' not in entry:
            continue
        
        # Extract satisfiability
        satisfiable = 'UNSATISFIABLE' if 'UNSATISFIABLE' in entry else 'SATISFIABLE'
        
        # Extract times
        solving_time_match = re.search(r'Solving Time\(ms\):\s*([\d.]+)', entry)
        total_time_match = re.search(r'Total time\(ms\):\s*([\d.]+)', entry)
        
        if solving_time_match and total_time_match:
            results.append({
                'formula': formula,
                'satisfiable': satisfiable,
                'solve_time': solving_time_match.group(1),
                'total_time': total_time_match.group(1),
                'solver': 'S52SAT'
            })
    
    return results


def parse_lcks5_file(filepath: str) -> List[Dict[str, str]]:
    """Parse LCKS5 benchmark file."""
    results = []
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split by FORMULA: entries
    entries = re.split(r'FORMULA:\s*', content)[1:]  # Skip first empty split
    
    for entry in entries:
        lines = entry.strip().split('\n')
        if not lines:
            continue
            
        formula = lines[0].strip()
        
        # Check for out of memory
        if 'Out of Memory' in entry:
            results.append({
                'formula': formula,
                'satisfiable': 'MEMORY',
                'solve_time': 'MEMORY',
                'total_time': 'MEMORY',
                'solver': 'LCKS5'
            })
            continue
        
        # Check for timeout
        if 'TIMEOUT' in entry:
            total_time_match = re.search(r'TOTAL TIME:\s*([\d.]+)', entry)
            total_time = '300000.0'  # Default 5 minutes in ms
            if total_time_match:
                total_time = str(float(total_time_match.group(1)) * 1000)  # Convert seconds to ms
            results.append({
                'formula': formula,
                'satisfiable': 'TIMEOUT',
                'solve_time': 'TIMEOUT',
                'total_time': total_time,
                'solver': 'LCKS5'
            })
            continue
        
        # Check if invalid (UNKNOWN)
        if 'UNKOWN' in entry or 'UNKNOWN' in entry:
            continue
        
        # Extract satisfiability
        satisfiable = 'UNSATISFIABLE' if 'UNSATISFIABLE' in entry else 'SATISFIABLE'
        
        # Extract time (in seconds, convert to ms)
        total_time_match = re.search(r'TOTAL TIME:\s*([\d.]+)', entry)
        
        if total_time_match:
            total_time_sec = float(total_time_match.group(1))
            total_time_ms = total_time_sec * 1000
            results.append({
                'formula': formula,
                'satisfiable': satisfiable,
                'solve_time': f'{total_time_ms:.6f}',  # Same as total time
                'total_time': f'{total_time_ms:.6f}',
                'solver': 'LCKS5'
            })
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Generate benchmark summary CSV from solver output files'
    )
    parser.add_argument(
        '--cegar',
        default='benchmark_CEGAR.txt',
        help='Path to CEGAR benchmark file (default: benchmark_CEGAR.txt)'
    )
    parser.add_argument(
        '--s52sat',
        default='benchmark_s52sat_diamondDegree_caching.txt',
        help='Path to S52SAT benchmark file (default: benchmark_s52sat_diamondDegree_caching.txt)'
    )
    parser.add_argument(
        '--lcks5',
        default='benchmark_LCKS5.txt',
        help='Path to LCKS5 benchmark file (default: benchmark_LCKS5.txt)'
    )
    parser.add_argument(
        '--output',
        default='benchmarks_summary.csv',
        help='Path to output CSV file (default: benchmarks_summary.csv)'
    )
    
    args = parser.parse_args()
    
    # Parse all files
    print(f"Parsing {args.cegar}...")
    cegar_results = parse_cegar_file(args.cegar)
    print(f"  Found {len(cegar_results)} valid entries")
    
    print(f"Parsing {args.s52sat}...")
    s52sat_results = parse_s52sat_file(args.s52sat)
    print(f"  Found {len(s52sat_results)} valid entries")
    
    print(f"Parsing {args.lcks5}...")
    lcks5_results = parse_lcks5_file(args.lcks5)
    print(f"  Found {len(lcks5_results)} valid entries")
    
    # Combine all results
    all_results = cegar_results + s52sat_results + lcks5_results
    
    # Write to CSV
    print(f"\nWriting {len(all_results)} total entries to {args.output}...")
    with open(args.output, 'w', newline='') as csvfile:
        fieldnames = ['formula', 'satisfiable', 'solve_time', 'total_time', 'solver']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"Done! Summary written to {args.output}")


if __name__ == '__main__':
    main()