#!/usr/bin/env python3
"""
CSV Benchmark Merger
Compares two CSV files and adds benchmark values from the first file to matching entries in the second file.
"""

import argparse
import csv


def read_csv_file(filepath: str, skip_rows: int = 2):
    """
    Read a CSV file and return data as a dictionary mapping formula to row data.
    
    Args:
        filepath: Path to the CSV file
        skip_rows: Number of header rows to skip (default: 2)
        
    Returns:
        Dictionary mapping formula to the entire row
    """
    formula_dict = {}
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    if len(lines) < skip_rows:
        return formula_dict
    
    # Skip header rows
    data_lines = lines[skip_rows:]
    reader = csv.reader(data_lines, delimiter=',')
    
    for row in reader:
        if not row or not row[0].strip():
            continue
        
        formula = row[0].strip()
        formula_dict[formula] = row
    
    return formula_dict


def merge_files(file1_path: str, file2_path: str, output_path: str):
    """
    Merge benchmark values from file1 into file2 based on matching formulas.
    
    Args:
        file1_path: Path to first CSV file (source of benchmark values)
        file2_path: Path to second CSV file (target file to be enhanced)
        output_path: Path to output CSV file
    """
    # Read both files
    print(f"Reading {file1_path}...")
    file1_data = read_csv_file(file1_path)
    print(f"  Found {len(file1_data)} formulas")
    
    print(f"Reading {file2_path}...")
    file2_data = read_csv_file(file2_path)
    print(f"  Found {len(file2_data)} formulas")
    
    # Process file2 and add benchmark values from file1
    matched_count = 0
    output_rows = []
    
    for formula, row in file2_data.items():
        if formula in file1_data:
            # Extract benchmark value from file1 (last column or specific index)
            file1_row = file1_data[formula]
            # Assuming benchmark is at index 5 based on the format:
            # formula, SAT, SAT, time, time, benchmark
            if len(file1_row) > 5:
                benchmark = file1_row[5].strip()
                # Add benchmark to the end of file2 row
                enhanced_row = row + [benchmark]
                output_rows.append(enhanced_row)
                matched_count += 1
            else:
                output_rows.append(row)
        else:
            # No match found, keep original row
            output_rows.append(row)
    
    print(f"\nMatched {matched_count} formulas")
    
    # Write output file
    print(f"Writing output to {output_path}...")
    with open(output_path, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=',')
        
        # Write header rows for file2 format
        writer.writerow(['formula', 'SATISFIABLE', 'SATISFIABLE', 'SATISFIABLE', 
                        'solve_time', 'solve_time', 'solve_time', 'benchmark'])
        writer.writerow(['', 'CEGAR', 'LCKS5', 'S52SAT', 'CEGAR', 'LCKS5', 'S52SAT', ''])
        
        # Write processed data
        writer.writerows(output_rows)
    
    print(f"Done! Output written to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Merge benchmark values from first CSV file into second CSV file based on matching formulas'
    )
    parser.add_argument(
        '--file1',
        '-f1',
        required=True,
        help='Path to first CSV file (2 solvers: CEGAR, S52SAT)'
    )
    parser.add_argument(
        '--file2',
        '-f2',
        required=True,
        help='Path to second CSV file (3 solvers: CEGAR, LCKS5, S52SAT)'
    )
    parser.add_argument(
        '--output',
        '-o',
        default='merged_output.csv',
        help='Path to output CSV file (default: merged_output.csv)'
    )
    
    args = parser.parse_args()
    
    merge_files(args.file1, args.file2, args.output)


if __name__ == '__main__':
    main()