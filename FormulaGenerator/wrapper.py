#!/usr/bin/env python3
"""
InToHyLo Format Converter

Converts InToHyLo formulas to different formats:
- S52SAT: Adds begin/end markers
- LCKS5: Decrements all indices by 1
- CEGAR: Removes all indices
"""

import re
import argparse
import sys
import os


def convert_to_s52sat(formula):
    """
    Convert formula to S52SAT format.
    Adds 'begin' before and 'end' after the formula.
    
    Args:
        formula: InToHyLo formula string
        
    Returns:
        Formula with begin/end markers
    """
    result = re.sub(r'\[(\d+)\]', r'[r\1]', formula)
    return f"begin\n{result.strip()}\nend"


def convert_to_lcks5(formula):
    """
    Convert formula to LCKS5 format.
    Decrements all indices in [i] and <i> by 1.
    
    Args:
        formula: InToHyLo formula string
        
    Returns:
        Formula with decremented indices
    """
    def decrement_bracket(match):
        idx = int(match.group(1))
        new_idx = idx - 1
        return f'[{new_idx}]'
    
    def decrement_angle(match):
        idx = int(match.group(1))
        new_idx = idx - 1
        return f'<{new_idx}>'
    
    def decrement_at(match):
        idx = int(match.group(1))
        new_idx = idx - 1
        return f'@_{new_idx}'
    
    result = formula
    result = re.sub(r'\[(\d+)\]', decrement_bracket, result)
    result = re.sub(r'<(\d+)>', decrement_angle, result)
    # result = re.sub(r'@_(\d+)', decrement_at, result)
    
    return result


def convert_to_cegar(formula):
    """
    Convert formula to CEGAR format.
    Removes all indices from [i] and <i>.
    
    Args:
        formula: InToHyLo formula string
        
    Returns:
        Formula with indices removed
    """
    result = formula
    result = re.sub(r'\[\d+\]', '[]', result)
    result = re.sub(r'<\d+>', '<>', result)
    # result = re.sub(r'@_\d+', '@_', result)
    
    return result


def parse_formulas(text):
    """
    Parse multiple formulas from input text.
    Formulas are separated by newlines.
    
    Args:
        text: String containing one or more formulas
        
    Returns:
        List of formula strings
    """
    lines = text.strip().split('\n')
    formulas = []
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):  # Skip empty lines and comments
            formulas.append(line)
    
    return formulas


def process_formulas(formulas, format_type):
    """
    Process multiple formulas with the specified format.
    
    Args:
        formulas: List of formula strings
        format_type: 'S52SAT', 'LCKS5', or 'CEGAR'
        
    Returns:
        List of converted formulas
    """
    converters = {
        'S52SAT': convert_to_s52sat,
        'LCKS5': convert_to_lcks5,
        'CEGAR': convert_to_cegar
    }
    
    converter = converters[format_type]
    return [converter(f) for f in formulas]


def write_output_files(formulas, output_base):
    """
    Write three output files with different formats.
    
    Args:
        formulas: List of formula strings
        output_base: Base name for output files (without extension)
    """
    formats = ['S52SAT', 'LCKS5', 'CEGAR']
    
    for fmt in formats:
        converted = process_formulas(formulas, fmt)
        
        # Determine output filename
        if output_base.endswith('.txt'):
            output_file = output_base.replace('.txt', f'_{fmt}.txt')
        else:
            output_file = f'{output_base}_{fmt}.txt'
        
        # Write to file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                if fmt == 'S52SAT':
                    # For S52SAT, each formula has begin/end
                    for converted_formula in converted:
                        f.write(converted_formula + '\n\n')
                else:
                    # For LCKS5 and CEGAR, one formula per line
                    for converted_formula in converted:
                        f.write(converted_formula + '\n')
            
            print(f"✓ Created {output_file} ({len(converted)} formula(s))")
        except Exception as e:
            print(f"✗ Error writing {output_file}: {e}")
            sys.exit(1)


def interactive_mode():
    """Run the converter in interactive mode."""
    print("Interactive Mode - InToHyLo Format Converter")
    print("Enter an InToHyLo formula (or 'quit' to exit):")
    print()
    
    while True:
        try:
            user_input = input("> ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_input.strip():
                print("\nS52SAT format:")
                print(convert_to_s52sat(user_input))
                print("\nLCKS5 format:")
                print(convert_to_lcks5(user_input))
                print("\nCEGAR format:")
                print(convert_to_cegar(user_input))
                print()
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


def show_examples():
    """Display example conversions."""
    examples = [
        "[1] (p4 | p3) & <1> ~p1",
        "[2] (p1 & p2)",
        "[3] p5 & [3] p6"
    ]
    
    print("Example Conversions:")
    print("=" * 60)
    
    for i, formula in enumerate(examples, 1):
        print(f"\nExample {i}:")
        print(f"Input:    {formula}")
        print(f"\nS52SAT:   {convert_to_s52sat(formula).replace(chr(10), '\n')}")
        print(f"LCKS5:    {convert_to_lcks5(formula)}")
        print(f"CEGAR:    {convert_to_cegar(formula)}")
        print("-" * 60)


def main():
    """Main function with CLI argument parsing."""
    
    parser = argparse.ArgumentParser(
        description='Convert InToHyLo formulas to S52SAT, LCKS5, and CEGAR formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -f "[1] p1" -o output.txt
  %(prog)s -i input.txt -o output.txt
  %(prog)s --interactive
  %(prog)s --examples

Output:
  Creates three files: output_S52SAT.txt, output_LCKS5.txt, output_CEGAR.txt
        """
    )
    
    parser.add_argument('-f', '--formula', type=str,
                        help='InToHyLo formula to convert')
    parser.add_argument('-i', '--input', type=str,
                        help='Input file containing InToHyLo formulas')
    parser.add_argument('-o', '--output', type=str,
                        help='Base name for output files')
    parser.add_argument('--interactive', action='store_true',
                        help='Run in interactive mode')
    parser.add_argument('--examples', action='store_true',
                        help='Show example conversions')
    
    args = parser.parse_args()
    
    # If no arguments, show examples by default
    if len(sys.argv) == 1:
        args.examples = True
    
    # Show examples
    if args.examples:
        show_examples()
        return
    
    # Interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    # Process formulas
    formulas = []
    
    if args.formula:
        formulas = [args.formula]
        print(f"Processing 1 formula from command line")
    elif args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                content = f.read()
            formulas = parse_formulas(content)
            print(f"Processing {len(formulas)} formula(s) from: {args.input}")
        except FileNotFoundError:
            print(f"Error: File '{args.input}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        return
    
    if not formulas:
        print("Error: No formulas to process")
        sys.exit(1)
    
    # Determine output base name
    if args.output:
        output_base = args.output
    elif args.input:
        # Use input filename as base
        output_base = os.path.splitext(args.input)[0] + '_output.txt'
    else:
        output_base = 'output.txt'
    
    # Write output files
    print()
    write_output_files(formulas, output_base)
    print()
    print(f"✓ All conversions complete!")


if __name__ == "__main__":
    main()