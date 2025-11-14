#!/usr/bin/env python3
"""
Formula Generation Pipeline Script

Runs the complete pipeline:
1. generator.py - Generates modal logic formulas
2. converter.py - Converts to InToHyLo format
3. wrapper.py - Creates S52SAT, LCKS5, and CEGAR output files
"""

import argparse
import subprocess
import sys
import os


def run_command(cmd, description):
    """
    Run a command and handle errors.
    
    Args:
        cmd: List of command arguments
        description: Description of the step for error messages
    """
    print(f"→ {description}...")
    print(f"  Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        print(f"✓ {description} completed\n")
        return result
    except subprocess.CalledProcessError as e:
        print(f"✗ Error in {description}:", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"✗ Error: Could not find script - {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function with CLI argument parsing."""
    
    parser = argparse.ArgumentParser(
        description='Run the complete formula generation and conversion pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Pipeline Steps:
  1. generator.py  - Generate modal logic formulas
  2. converter.py  - Convert to InToHyLo format
  3. wrapper.py    - Create S52SAT, LCKS5, and CEGAR files

Examples:
  # Basic usage with default parameters
  %(prog)s -o formulas.txt
  
  # Generate 10 formulas with depth 3
  %(prog)s -o formulas.txt --count 10 -d 3
  
  # Custom parameters
  %(prog)s -o formulas.txt -d 2 -L 5 -N 6 -m 2 --count 5
  
  # With custom distributions
  %(prog)s -o formulas.txt -C "[[0,2,2],[2,4],[6]]" --count 3
        """
    )
    
    # Output file (required)
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='Output file base name (required)')
    
    # Generator parameters
    parser.add_argument('-d', '--depth', type=int, default=2,
                        help='Modal depth (default: 2)')
    parser.add_argument('-L', '--clauses', type=int, default=4,
                        help='Number of clauses (default: 4)')
    parser.add_argument('-N', '--variables', type=int, default=4,
                        help='Number of propositional variables (default: 4)')
    parser.add_argument('-m', '--boxes', type=int, default=1,
                        help='Number of box symbols (default: 1)')
    parser.add_argument('-C', '--clause-dist', type=str, default='[[0,2,2],[2,4],[6]]',
                        help='Clause length distribution (default: [[0,2,2],[2,4],[6]])')
    parser.add_argument('-p', '--prop-dist', type=str, 
                        default='[[[0],[0,2,0],[0,2,0,0]],[[2,0],[0,4,0]],[]]',
                        help='Propositional/modal rate distribution')
    parser.add_argument('--count', type=int, default=1,
                        help='Number of formulas to generate (default: 1)')
    parser.add_argument('--seed', type=int,
                        help='Random seed for reproducibility')
    
    # Script locations (optional)
    parser.add_argument('--generator', type=str, default='generator.py',
                        help='Path to generator.py (default: generator.py)')
    parser.add_argument('--converter', type=str, default='converter.py',
                        help='Path to converter.py (default: converter.py)')
    parser.add_argument('--wrapper', type=str, default='wrapper.py',
                        help='Path to wrapper.py (default: wrapper.py)')
    
    args = parser.parse_args()
    
    # Determine file names
    base_name = args.output
    if base_name.endswith('.txt'):
        base_name = base_name[:-4]
    
    generated_file = f"{base_name}_generated.txt"
    converted_file = f"{base_name}_intohylo.txt"
    
    print("=" * 70)
    print("FORMULA GENERATION PIPELINE")
    print("=" * 70)
    print(f"Output base name: {base_name}")
    print(f"Generated file:   {generated_file}")
    print(f"Converted file:   {converted_file}")
    print(f"Final files:      {base_name}_intohylo_S52SAT.txt")
    print(f"                  {base_name}_intohylo_LCKS5.txt")
    print(f"                  {base_name}_intohylo_CEGAR.txt")
    print("=" * 70)
    print()
    
    # Step 1: Run generator.py
    # First 5 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '1',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[1,0],[1,0]]',
        '-p', '[[[1,1]],[[0,1]]]',
        '--count', '5',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 5 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '1',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[0,1],[0,1]]',
        '-p', '[[[1,1],[1,2,1]],[[1,1],[1,2,1]]]',
        '--count', '5',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 5 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '1',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[0,0,1],[0,0,1]]',
        '-p', '[[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]]]',
        '--count', '5',
        '-o', generated_file
    ]
    
    # Next 5 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '1',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[0,1,1],[0,1,1]]',
        '-p', '[[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]]]',
        '--count', '5',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 5 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '1',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[1,0,1],[1,0,1]]',
        '-p', '[[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]]]',
        '--count', '5',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 5 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '1',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[1,1,1],[1,1,1]]',
        '-p', '[[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]]]',
        '--count', '5',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 5 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '2',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[0,1],[0,1],[0,1]]',
        '-p', '[[[1,1],[1,2,1]],[[1,1],[1,2,1]],[[1,1],[1,2,1]]]',
        '--count', '5',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 5 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '2',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[0,0,1],[0,0,1],[0,0,1]]',
        '-p', '[[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]]]',
        '--count', '5',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }

    # Next 5 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '2',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[0,1,1],[0,1,1],[0,1,1]]',
        '-p', '[[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]]]',
        '--count', '5',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 5 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '2',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[1,0,1],[1,0,1],[1,0,1]]',
        '-p', '[[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]]]',
        '--count', '5',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 5 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '2',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[1,1,1],[1,1,1],[1,1,1]]',
        '-p', '[[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]]]',
        '--count', '5',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 5 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '3',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[0,1],[0,1],[0,1],[0,1]]',
        '-p', '[[[1,1],[1,2,1]],[[1,1],[1,2,1]],[[1,1],[1,2,1]],[[1,1],[1,2,1]]]',
        '--count', '5',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 5 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '3',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[0,0,1],[0,0,1],[0,0,1],[0,0,1]]',
        '-p', '[[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]]]',
        '--count', '5',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 5 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '3',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[0,0,1],[0,0,1],[0,0,1],[0,0,1]]',
        '-p', '[[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]]]',
        '--count', '5',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 5 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '3',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[0,1,1],[0,1,1],[0,1,1],[0,1,1]]',
        '-p', '[[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]]]',
        '--count', '5',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 5 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '3',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[1,0,1],[1,0,1],[1,0,1],[1,0,1]]',
        '-p', '[[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]]]',
        '--count', '5',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 5 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '3',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[1,1,1],[1,1,1],[1,1,1],[1,1,1]]',
        '-p', '[[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]],[[1,1],[1,2,1],[1,3,3,1]]]',
        '--count', '5',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 15 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '2',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[0,1,1],[1,2],[1]]',
        '-p', '[[[],[0,2,0],[0,2,0,0]],[[2,0],[0,4,0]],[]]',
        '--count', '15',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 15 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '3',
        '-L', '4',
        '-N', '3',
        '-m', '1',
        '-C', '[[1,8,1],[],[],[]]',
        '-p', '[[[1,0],[0,1,0],[0,1,1,0]],[],[],[]]',
        '--count', '15',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 15 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '3',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[1,8,1],[],[],[]]',
        '-p', '[[[1,0],[0,1,0],[0,1,1,0]],[],[],[]]',
        '--count', '15',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 15 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '4',
        '-L', '4',
        '-N', '3',
        '-m', '1',
        '-C', '[[1,8,1],[],[],[],[]]',
        '-p', '[[[1,0],[0,1,0],[0,1,1,0]],[],[],[],[]]',
        '--count', '15',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 15 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '4',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[1,8,1],[],[],[],[]]',
        '-p', '[[[1,0],[0,1,0],[0,1,1,0]],[],[],[],[]]',
        '--count', '15',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 15 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '4',
        '-L', '4',
        '-N', '3',
        '-m', '1',
        '-C', '[[1,8,1],[1,2],[],[],[]]',
        '-p', '[[[1,0],[0,1,0],[0,1,1,0]],[[1,0],[0,1,0]],[],[],[]]',
        '--count', '15',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 15 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '4',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[1,8,1],[1,2],[],[],[]]',
        '-p', '[[[1,0],[0,1,0],[0,1,1,0]],[[1,0],[0,1,0]],[],[],[]]',
        '--count', '15',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 15 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '4',
        '-L', '4',
        '-N', '5',
        '-m', '1',
        '-C', '[[1,8,1],[1,2],[],[],[]]',
        '-p', '[[[1,0],[0,1,0],[0,1,1,0]],[[1,0],[0,1,0]],[],[],[]]',
        '--count', '15',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 15 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '5',
        '-L', '4',
        '-N', '3',
        '-m', '1',
        '-C', '[[1,8,1],[1,2],[],[],[],[]]',
        '-p', '[[[1,0],[0,1,0],[0,1,1,0]],[[1,0],[0,1,0]],[],[],[],[]]',
        '--count', '15',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 15 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '5',
        '-L', '4',
        '-N', '4',
        '-m', '1',
        '-C', '[[1,8,1],[1,2],[],[],[],[]]',
        '-p', '[[[1,0],[0,1,0],[0,1,1,0]],[[1,0],[0,1,0]],[],[],[],[]]',
        '--count', '15',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    # Next 15 tests
    # {
    generator_cmd = [
        'python3', args.generator,
        '-d', '5',
        '-L', '4',
        '-N', '5',
        '-m', '1',
        '-C', '[[1,8,1],[1,2],[],[],[],[]]',
        '-p', '[[[1,0],[0,1,0],[0,1,1,0]],[[1,0],[0,1,0]],[],[],[],[]]',
        '--count', '15',
        '-o', generated_file
    ]
    
    if args.seed is not None:
        generator_cmd.extend(['--seed', str(args.seed)])
    run_command(generator_cmd, "Step 1: Generating formulas")
    # }
    
    # Verify generated file exists
    if not os.path.exists(generated_file):
        print(f"✗ Error: Generated file {generated_file} not found", file=sys.stderr)
        sys.exit(1)
    
    # Step 2: Run converter.py
    converter_cmd = [
        'python3', args.converter,
        '-i', generated_file,
        '-o', converted_file
    ]
    
    run_command(converter_cmd, "Step 2: Converting to InToHyLo format")
    
    # Verify converted file exists
    if not os.path.exists(converted_file):
        print(f"✗ Error: Converted file {converted_file} not found", file=sys.stderr)
        sys.exit(1)
    
    # Step 3: Run wrapper.py
    wrapper_cmd = [
        'python3', args.wrapper,
        '-i', converted_file,
        '-o', converted_file
    ]
    
    run_command(wrapper_cmd, "Step 3: Creating S52SAT, LCKS5, and CEGAR files")
    
    # Verify final files exist
    final_files = [
        f"{base_name}_intohylo_S52SAT.txt",
        f"{base_name}_intohylo_LCKS5.txt",
        f"{base_name}_intohylo_CEGAR.txt"
    ]
    
    print("=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)
    print(f"\n✓ Generated {args.count} formula(s)")
    print(f"\nIntermediate files:")
    print(f"  • {generated_file}")
    print(f"  • {converted_file}")
    print(f"\nFinal output files:")
    for f in final_files:
        if os.path.exists(f):
            print(f"  ✓ {f}")
        else:
            print(f"  ✗ {f} (not found)")
    print()


if __name__ == "__main__":
    main()