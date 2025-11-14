#!/usr/bin/env python3
"""
LCK Benchmark Runner

Runs LCK on formulas and extracts benchmark results.
Processes LCKS5 format files and saves timing information.
"""

import argparse
import subprocess
import sys
import os
import re
import time


def parse_lck_output(output):
    """
    Parse LCK output and extract satisfiability status.
    
    Args:
        output: String containing LCK output
        
    Returns:
        'SATISFIABLE', 'UNSATISFIABLE', or None
    """
    # Look for SATISFIABLE or UNSATISFIABLE in output
    if re.search(r'\bSATISFIABLE\b', output, re.IGNORECASE):
        return 'SATISFIABLE'
    elif re.search(r'\bUNSATISFIABLE\b', output, re.IGNORECASE):
        return 'UNSATISFIABLE'
    
    # Sometimes the output might be lowercase or with different formatting
    if re.search(r'\bsat\b', output, re.IGNORECASE) and not re.search(r'\bunsat\b', output, re.IGNORECASE):
        return 'SATISFIABLE'
    elif re.search(r'\bunsat\b', output, re.IGNORECASE):
        return 'UNSATISFIABLE'
    
    return None


def run_lck_on_formula(formula, lck_path, verbose=False):
    """
    Run LCK on a single formula using echo | lck graph.
    
    Args:
        formula: The formula string
        lck_path: Path to LCK executable
        verbose: Whether to print verbose output
        
    Returns:
        Tuple of (status, total_time)
    """
    try:
        # Build command: echo "formula" | ./lck graph
        cmd = f'echo "{formula}" | {lck_path} graph'
        
        if verbose:
            print(f"    Running: {cmd[:100]}{'...' if len(cmd) > 100 else ''}")
        
        # Run LCK and time it
        start_time = time.time()
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        end_time = time.time()
        total_time = end_time - start_time
        
        # Get output
        output = result.stdout + result.stderr
        
        # Parse status
        status = parse_lck_output(output)
        
        if verbose:
            print(f"    Status: {status}")
            print(f"    Time: {total_time:.6f}s")
        
        return status, total_time
        
    except subprocess.TimeoutExpired:
        print(f"    WARNING: Timeout on formula", file=sys.stderr)
        return 'TIMEOUT', 300.0
    except Exception as e:
        print(f"    ERROR: {e}", file=sys.stderr)
        return 'ERROR', 0.0


def format_results(formula, status, total_time):
    """
    Format the results for output.
    
    Args:
        formula: The formula string
        status: SATISFIABLE, UNSATISFIABLE, or error status
        total_time: Total execution time in seconds
        
    Returns:
        Formatted string for output
    """
    lines = []
    lines.append(f"FORMULA: {formula}")
    
    if status:
        lines.append(status)
    else:
        lines.append("UNKNOWN")
    
    lines.append(f"TOTAL TIME: {total_time:.6f}")
    
    return '\n'.join(lines)


def read_formulas(filename):
    """
    Read formulas from a file.
    
    Args:
        filename: Path to file containing formulas
        
    Returns:
        List of formula strings
    """
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    formulas = []
    lines = content.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            formulas.append(line)
    
    return formulas


def main():
    """Main function with CLI argument parsing."""
    
    parser = argparse.ArgumentParser(
        description='Run LCK on LCKS5 format formulas and benchmark results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i formulas_intohylo_LCKS5.txt
  %(prog)s -i formulas_intohylo_LCKS5.txt -o benchmark_LCKS5.txt
  %(prog)s -i formulas_intohylo_LCKS5.txt --lck ./lck --verbose
        """
    )
    
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='Input file with LCKS5 format formulas (required)')
    parser.add_argument('-o', '--output', type=str,
                        help='Output file for benchmark results (default: benchmark_LCKS5.txt)')
    parser.add_argument('--lck', type=str, default='./lck',
                        help='Path to LCK executable (default: ./lck)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print verbose output')
    
    args = parser.parse_args()
    
    # Determine output filename
    if args.output:
        output_file = args.output
    else:
        output_file = 'benchmark_LCKS5.txt'
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Check if LCK executable exists
    if not os.path.exists(args.lck):
        print(f"Warning: LCK executable '{args.lck}' not found at specified path", file=sys.stderr)
        print(f"Will attempt to run anyway...", file=sys.stderr)
    
    # Read formulas
    print(f"Reading formulas from: {args.input}")
    try:
        formulas = read_formulas(args.input)
        print(f"Found {len(formulas)} formula(s)\n")
    except Exception as e:
        print(f"Error reading formulas: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Process each formula
    results = []
    
    for i, formula in enumerate(formulas, 1):
        print(f"Processing formula {i}/{len(formulas)}...")
        if args.verbose:
            print(f"  Formula: {formula[:60]}{'...' if len(formula) > 60 else ''}")
        
        status, total_time = run_lck_on_formula(
            formula, 
            args.lck,
            args.verbose
        )
        
        formatted_result = format_results(formula, status, total_time)
        results.append(formatted_result)
        
        print(f"✓ Formula {i} complete: {status}\n")
    
    # Write results to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(results))
            f.write('\n')
        
        print(f"✓ Results written to: {output_file}")
        print(f"✓ Processed {len(formulas)} formula(s)")
        
    except Exception as e:
        print(f"Error writing results: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()