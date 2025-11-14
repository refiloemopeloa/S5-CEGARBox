#!/usr/bin/env python3
"""
s52sat Benchmark Runner

Runs s52sat on formulas with different configurations and extracts benchmark results.
Processes s52sat format files and saves timing information.
"""

import argparse
import subprocess
import sys
import os
import re
import tempfile


def parse_s52sat_output(output):
    """
    Parse s52sat output and extract relevant information.
    
    Args:
        output: String containing s52sat output
        
    Returns:
        Dictionary with extracted information
    """
    result = {
        'parsing_time': None,
        's5_simplification_time': None,
        'transform_cnf_time': None,
        'load_cnf_time': None,
        'cleaning_data_time': None,
        'solving_time': None,
        'status': None,
        'kripke_output_time': None,
        'total_time': None
    }
    
    # Extract timing information
    timing_patterns = {
        'parsing_time': r'Parsing time\(ms\):\s*([0-9.]+)',
        's5_simplification_time': r'S5 Simplification time\(ms\):\s*([0-9.]+)',
        'transform_cnf_time': r'Transform CNF time\(ms\):\s*([0-9.]+)',
        'load_cnf_time': r'Load CNF time\(ms\):\s*([0-9.]+)',
        'cleaning_data_time': r'Cleaning Data time\(ms\):\s*([0-9.]+)',
        'solving_time': r'Solving Time\(ms\):\s*([0-9.]+)',
        'kripke_output_time': r'Kripke output Time\(ms\):\s*([0-9.]+)',
        'total_time': r'Total time\(ms\):\s*([0-9.]+)'
    }
    
    for key, pattern in timing_patterns.items():
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            result[key] = match.group(1)
    
    # Extract status (SATISFIABLE or UNSATISFIABLE)
    status_match = re.search(r'(SATISFIABLE|UNSATISFIABLE)', output, re.IGNORECASE)
    if status_match:
        result['status'] = status_match.group(1).upper()
    
    return result


def format_results(formula, parsed_output):
    """
    Format the results for output.
    
    Args:
        formula: The formula string
        parsed_output: Dictionary with parsed s52sat output
        
    Returns:
        Formatted string for output
    """
    lines = []
    lines.append(f"FORMULA: {formula}")
    
    timing_keys = [
        ('parsing_time', 'Parsing time(ms)'),
        ('s5_simplification_time', 'S5 Simplification time(ms)'),
        ('transform_cnf_time', 'Transform CNF time(ms)'),
        ('load_cnf_time', 'Load CNF time(ms)'),
        ('cleaning_data_time', 'Cleaning Data time(ms)'),
        ('solving_time', 'Solving Time(ms)')
    ]
    
    for key, label in timing_keys:
        if parsed_output[key]:
            lines.append(f"{label}: {parsed_output[key]}")
    
    if parsed_output['status']:
        lines.append(parsed_output['status'])
    
    if parsed_output['kripke_output_time']:
        lines.append(f"Kripke output Time(ms): {parsed_output['kripke_output_time']}")
    
    if parsed_output['total_time']:
        lines.append(f"Total time(ms): {parsed_output['total_time']}")
    
    return '\n'.join(lines)


def run_s52sat_on_formula(formula, s52sat_path, cli_args, verbose=False):
    """
    Run s52sat on a single formula.
    
    Args:
        formula: The formula string (with begin/end markers)
        s52sat_path: Path to s52sat executable
        cli_args: List of additional CLI arguments
        verbose: Whether to print verbose output
        
    Returns:
        Parsed output dictionary
    """
    # Create temporary file for the formula
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
        tmp.write('begin\n')
        tmp.write(formula)
        tmp.write('\nend\n')
        tmp_filename = tmp.name
    
    try:
        # Build command
        cmd = [s52sat_path, tmp_filename] + cli_args
        
        if verbose:
            print(f"    Running: {' '.join(cmd)}")
        
        # Run s52sat
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        # Get output
        output = result.stdout + result.stderr
        
        # Parse output
        parsed = parse_s52sat_output(output)
        
        if verbose:
            print(f"    Status: {parsed.get('status', 'Unknown')}")
        
        return parsed
        
    except subprocess.TimeoutExpired:
        print(f"    WARNING: Timeout on formula", file=sys.stderr)
        return {
            'parsing_time': None,
            's5_simplification_time': None,
            'transform_cnf_time': None,
            'load_cnf_time': None,
            'cleaning_data_time': None,
            'solving_time': None,
            'status': 'Timeout',
            'kripke_output_time': None,
            'total_time': None
        }
    except Exception as e:
        print(f"    ERROR: {e}", file=sys.stderr)
        return {
            'parsing_time': None,
            's5_simplification_time': None,
            'transform_cnf_time': None,
            'load_cnf_time': None,
            'cleaning_data_time': None,
            'solving_time': None,
            'status': 'Error',
            'kripke_output_time': None,
            'total_time': None
        }
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)


def extract_formula_results(output, formulas):
    """
    Extract results for each formula from s52sat output.
    
    Since s52sat processes multiple formulas in one file, we need to
    parse the output and match results to formulas.
    
    Args:
        output: Complete s52sat output
        formulas: List of formula strings
        
    Returns:
        List of parsed outputs (one per formula)
    """
    results = []
    
    # Split output into sections (one per formula)
    # s52sat typically outputs results sequentially
    sections = re.split(r'(?=Parsing time\(ms\):)', output)
    
    for i, section in enumerate(sections):
        if section.strip():
            parsed = parse_s52sat_output(section)
            results.append(parsed)
    
    # If we didn't get enough results, pad with empty results
    while len(results) < len(formulas):
        results.append({
            'parsing_time': None,
            's5_simplification_time': None,
            'transform_cnf_time': None,
            'load_cnf_time': None,
            'cleaning_data_time': None,
            'solving_time': None,
            'status': 'Error',
            'kripke_output_time': None,
            'total_time': None
        })
    
    return results[:len(formulas)]


def read_formulas_with_markers(filename):
    """
    Read formulas from s52sat format file (with begin/end markers).
    
    Args:
        filename: Path to file containing formulas
        
    Returns:
        List of formula strings (without begin/end markers)
    """
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    formulas = []
    
    # Split by 'begin' and 'end' markers
    sections = re.split(r'\bbegin\b', content)
    
    for section in sections[1:]:  # Skip first empty section
        # Extract content between begin and end
        match = re.search(r'(.*?)\bend\b', section, re.DOTALL)
        if match:
            formula = match.group(1).strip()
            if formula:
                formulas.append(formula)
    
    return formulas


def run_configuration(input_file, s52sat_path, cli_args, output_file, config_name, verbose=False):
    """
    Run s52sat with a specific configuration and save results.
    
    Args:
        input_file: Path to input file
        s52sat_path: Path to s52sat executable
        cli_args: List of CLI arguments for this configuration
        output_file: Path to output file
        config_name: Name of configuration for display
        verbose: Whether to print verbose output
    """
    print(f"\n{'='*70}")
    print(f"Configuration: {config_name}")
    print(f"CLI Args: {' '.join(cli_args)}")
    print(f"Output: {output_file}")
    print(f"{'='*70}")
    
    # Read formulas
    try:
        formulas = read_formulas_with_markers(input_file)
        print(f"Found {len(formulas)} formula(s)")
    except Exception as e:
        print(f"Error reading formulas: {e}", file=sys.stderr)
        return
    
    # Run s52sat on each formula separately
    print(f"Running s52sat on each formula...")
    parsed_results = []
    
    for i, formula in enumerate(formulas, 1):
        print(f"  Processing formula {i}/{len(formulas)}...")
        if verbose:
            print(f"    Formula: {formula[:60]}{'...' if len(formula) > 60 else ''}")
        
        parsed = run_s52sat_on_formula(formula, s52sat_path, cli_args, verbose)
        parsed_results.append(parsed)
        
        print(f"  ✓ Formula {i} complete: {parsed.get('status', 'Unknown')}")
    
    # Format and write results
    formatted_results = []
    for formula, parsed in zip(formulas, parsed_results):
        formatted = format_results(formula, parsed)
        formatted_results.append(formatted)
    
    # Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(formatted_results))
            f.write('\n')
        
        print(f"✓ Results written to: {output_file}")
        print(f"✓ Processed {len(formulas)} formula(s)")
        
    except Exception as e:
        print(f"Error writing results: {e}", file=sys.stderr)


def main():
    """Main function with CLI argument parsing."""
    
    parser = argparse.ArgumentParser(
        description='Run s52sat on formulas with different configurations and benchmark results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configurations:
  1. -nbModals                  → benchmark_s52sat_nbModals.txt
  2. -nbModals -caching         → benchmark_s52sat_nbModals_caching.txt
  3. -diamondDegree             → benchmark_s52sat_diamondDegree.txt
  4. -diamondDegree -caching    → benchmark_s52sat_diamondDegree_caching.txt

Examples:
  %(prog)s -i formulas_intohylo_s52sat.txt
  %(prog)s -i formulas_intohylo_s52sat.txt --s52sat ./s52sat
  %(prog)s -i formulas_intohylo_s52sat.txt -v
        """
    )
    
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='Input file with s52sat format formulas (required)')
    parser.add_argument('--s52sat', type=str, default='./s52sat',
                        help='Path to s52sat executable (default: s52sat)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print verbose output')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    print(f"{'='*70}")
    print(f"s52sat BENCHMARK RUNNER")
    print(f"{'='*70}")
    print(f"Input file: {args.input}")
    print(f"s52sat executable: {args.s52sat}")
    
    # Configuration 1: -nbModals
    run_configuration(
        args.input,
        args.s52sat,
        ['-nbModals'],
        'benchmark_s52sat_nbModals.txt',
        'nbModals',
        args.verbose
    )
    
    # Configuration 2: -nbModals -caching
    run_configuration(
        args.input,
        args.s52sat,
        ['-nbModals', '-caching'],
        'benchmark_s52sat_nbModals_caching.txt',
        'nbModals + caching',
        args.verbose
    )
    
    # Configuration 3: -diamondDegree
    run_configuration(
        args.input,
        args.s52sat,
        ['-diamondDegree'],
        'benchmark_s52sat_diamondDegree.txt',
        'diamondDegree',
        args.verbose
    )
    
    # Configuration 4: -diamondDegree -caching
    run_configuration(
        args.input,
        args.s52sat,
        ['-diamondDegree', '-caching'],
        'benchmark_s52sat_diamondDegree_caching.txt',
        'diamondDegree + caching',
        args.verbose
    )
    
    print(f"\n{'='*70}")
    print(f"✓ ALL BENCHMARKS COMPLETE")
    print(f"{'='*70}")
    print(f"\nGenerated files:")
    print(f"  • benchmark_s52sat_nbModals.txt")
    print(f"  • benchmark_s52sat_nbModals_caching.txt")
    print(f"  • benchmark_s52sat_diamondDegree.txt")
    print(f"  • benchmark_s52sat_diamondDegree_caching.txt")
    print()


if __name__ == "__main__":
    main()