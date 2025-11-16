#!/usr/bin/env python3
"""
CSV Formula Counter
Processes a CSV file with modal logic formulas and adds modality depth and clause count.
"""

import argparse
import csv
import re


def count_modalities(formula: str) -> int:
    """
    Count the number of modality operators [r1] in a formula.
    
    Args:
        formula: The modal logic formula string
        
    Returns:
        The count of [r1] and <r1> occurrences
    """
    return formula.count('r1')


def count_clauses(formula: str) -> int:
    """
    Count the number of clauses in a formula (number of & + 1).
    
    Args:
        formula: The modal logic formula string
        
    Returns:
        The number of clauses (count of '&' + 1)
    """
    return formula.count('&') + 1


def process_csv(input_file: str, output_file: str):
    """
    Process the input CSV file and add modality depth and clause count columns.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
    """
    with open(input_file, 'r') as infile:
        # Read all lines
        lines = infile.readlines()
    
    if len(lines) < 2:
        print("Error: Input file must have at least 2 header rows")
        return
    
    # Skip first two header rows
    data_lines = lines[2:]
    
    # Parse the data rows
    reader = csv.reader(data_lines, delimiter=',')
    processed_rows = []
    
    for row in reader:
        if not row or not row[0].strip():
            continue
        
        formula = row[0].strip()
        
        # Count modalities and clauses
        depth = count_modalities(formula)
        num_clauses = count_clauses(formula)
        
        # Add depth and clause count to the row
        # Assuming the row structure is:
        # formula, SAT1, SAT2, time1, time2, benchmark, ...
        # We need to append depth and num_clauses at the end
        processed_row = row + [str(depth), str(num_clauses)]
        processed_rows.append(processed_row)
    
    # Write output CSV
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=',')
        
        # Write header rows
        writer.writerow(['formula', 'SATISFIABLE', 'SATISFIABLE', 'SATISFIABLE', 'solve_time', 'solve_time','solve_time', 'benchmark', 'd', 'N'])
        writer.writerow(['', 'CEGAR', 'LCKS5', 'S52SAT', 'CEGAR', 'LCKS5', 'S52SAT', '', '', ''])
        
        # Write processed data
        writer.writerows(processed_rows)
    
    print(f"Processed {len(processed_rows)} formulas")
    print(f"Output written to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Process modal logic formulas CSV and add modality depth and clause count'
    )
    parser.add_argument(
        '--input',
        '-i',
        required=True,
        help='Path to input CSV file'
    )
    parser.add_argument(
        '--output',
        '-o',
        default='output.csv',
        help='Path to output CSV file (default: output.csv)'
    )
    
    args = parser.parse_args()
    
    process_csv(args.input, args.output)


if __name__ == '__main__':
    main()