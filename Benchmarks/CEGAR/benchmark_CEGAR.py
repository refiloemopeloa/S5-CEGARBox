#!/usr/bin/env python3
"""
Kaleidoscope Benchmark Runner

Runs Kaleidoscope on formulas and extracts benchmark results.
Processes CEGAR format files and saves timing information.
"""

import argparse
import subprocess
import sys
import os
import re
import time
import tempfile


def parse_kaleidoscope_output(output):
    """
    Parse Kaleidoscope output and extract relevant information.
    
    Args:
        output: String containing Kaleidoscope output
        
    Returns:
        Dictionary with extracted information
    """
    result = {
        'status': None,
        'solved': None,
        'read_time': None,
        'parse_time': None,
        'nnf_time': None,
        'simplify_time': None,
        'flatten_time': None,
        'construct_time': None,
        'reduce_time': None,
        'prepare_time': None,
        'solve_time': None
    }
    
    # Extract status (Satisfiable or Unsatisfiable)
    status_match = re.search(r'^(Satisfiable|Unsatisfiable)$', output, re.MULTILINE)
    if status_match:
        result['status'] = status_match.group(1)
    
    # Extract "Solved"
    if re.search(r'^Solved$', output, re.MULTILINE):
        result['solved'] = 'Solved'
    
    # Extract timing information
    timing_patterns = {
        'read_time': r'READ TIME:\s*([0-9.]+)',
        'parse_time': r'PARSE TIME:\s*([0-9.]+)',
        'nnf_time': r'NNF TIME:\s*([0-9.]+)',
        'simplify_time': r'SIMPLIFY TIME:\s*([0-9.]+)',
        'flatten_time': r'FLATTEN TIME:\s*([0-9.]+)',
        'construct_time': r'CONSTRUCT TIME:\s*([0-9.]+)',
        'reduce_time': r'REDUCE TIME:\s*([0-9.]+)',
        'prepare_time': r'PREPARE TIME:\s*([0-9.]+)',
        'solve_time': r'SOLVE TIME:\s*([0-9.]+)'
    }
    
    for key, pattern in timing_patterns.items():
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            result[key] = match.group(1)
    
    return result


def format_results(formula, parsed_output, total_time):
    """
    Format the results for output.
    
    Args:
        formula: The formula string
        parsed_output: Dictionary with parsed Kaleidoscope output
        total_time: Total execution time in seconds
        
    Returns:
        Formatted string for output
    """
    lines = []
    lines.append(f"FORMULA: {formula}")
    
    if parsed_output['status']:
        lines.append(parsed_output['status'])
    
    if parsed_output['solved']:
        lines.append(parsed_output['solved'])
    
    timing_keys = [
        ('read_time', 'READ TIME'),
        ('parse_time', 'PARSE TIME'),
        ('nnf_time', 'NNF TIME'),
        ('simplify_time', 'SIMPLIFY TIME'),
        ('flatten_time', 'FLATTEN TIME'),
        ('construct_time', 'CONSTRUCT TIME'),
        ('reduce_time', 'REDUCE TIME'),
        ('prepare_time', 'PREPARE TIME'),
        ('solve_time', 'SOLVE TIME')
    ]
    
    for key, label in timing_keys:
        if parsed_output[key]:
            lines.append(f"{label}: {parsed_output[key]}")
    
    lines.append(f"TOTAL TIME: {total_time:.6f}")
    
    return '\n'.join(lines)


def run_kaleidoscope_on_formula(formula, kaleidoscope_path, verbose=False):
    """
    Run Kaleidoscope on a single formula.
    
    Args:
        formula: The formula string
        kaleidoscope_path: Path to Kaleidoscope executable
        verbose: Whether to print verbose output
        
    Returns:
        Tuple of (parsed_output, total_time)
    """
    # Create temporary file for the formula
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
        tmp.write(formula)
        tmp_filename = tmp.name
    
    try:
        # Build command
        cmd = [
            kaleidoscope_path,
            '-f', tmp_filename,
            '-t',
            '--euclidean',
            '--verbose'
        ]
        
        if verbose:
            print(f"  Running: {' '.join(cmd)}")
        
        # Run Kaleidoscope and time it
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        end_time = time.time()
        total_time = end_time - start_time
        total_time *= 1000
        
        # Parse output
        output = result.stdout + result.stderr
        parsed_output = parse_kaleidoscope_output(output)
        
        if verbose:
            print(f"  Status: {parsed_output['status']}")
            print(f"  Total time: {total_time:.6f}s")
        
        return parsed_output, total_time
        
    except subprocess.TimeoutExpired:
        print(f"  WARNING: Timeout on formula", file=sys.stderr)
        return {
            'status': 'Timeout',
            'solved': None,
            'read_time': None, 'parse_time': None, 'nnf_time': None,
            'simplify_time': None, 'flatten_time': None, 'construct_time': None,
            'reduce_time': None, 'prepare_time': None, 'solve_time': None
        }, 300.0
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return {
            'status': 'Error',
            'solved': None,
            'read_time': None, 'parse_time': None, 'nnf_time': None,
            'simplify_time': None, 'flatten_time': None, 'construct_time': None,
            'reduce_time': None, 'prepare_time': None, 'solve_time': None
        }, 0.0
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)


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
        description='Run Kaleidoscope on CEGAR format formulas and benchmark results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i formulas_intohylo_CEGAR.txt
  %(prog)s -i formulas_intohylo_CEGAR.txt -o results_CEGAR.txt
  %(prog)s -i formulas_intohylo_CEGAR.txt --kaleidoscope ./kaleidoscope --verbose
        """
    )
    
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='Input file with CEGAR format formulas (required)')
    parser.add_argument('-o', '--output', type=str,
                        help='Output file for benchmark results (default: benchmark_CEGAR.txt)')
    parser.add_argument('--kaleidoscope', type=str, default='./kaleidoscope',
                        help='Path to Kaleidoscope executable (default: kaleidoscope)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print verbose output')
    
    args = parser.parse_args()
    
    # Determine output filename
    if args.output:
        output_file = args.output
    else:
        output_file = 'benchmark_CEGAR.txt'
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
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
        
        parsed_output, total_time = run_kaleidoscope_on_formula(
            formula, 
            args.kaleidoscope,
            args.verbose
        )
        
        formatted_result = format_results(formula, parsed_output, total_time)
        results.append(formatted_result)
        
        print(f"✓ Formula {i} complete\n")
    
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