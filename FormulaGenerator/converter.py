#!/usr/bin/env python3
"""
Modal Logic to InToHyLo Format Converter

Converts modal logic formulas with box operators (□) to InToHyLo format.
InToHyLo uses @_i and <i> notation for hybrid logic representation.
"""

import re
import argparse
import sys


def convert_to_intohylo(formula):
    """
    Convert a modal logic formula to InToHyLo format.
    
    Format conversions:
    - □i(φ) -> @_i [i] φ
    - ¬ -> ~
    - ∧ -> &
    - ∨ -> |
    - Ai -> pi (proposition variables)
    
    Args:
        formula: String containing modal logic formula
        
    Returns:
        String in InToHyLo format
    """
    # Remove extra whitespace
    formula = formula.strip()
    
    # Replace logical operators
    formula = formula.replace('¬', '~')
    formula = formula.replace('∧', '&')
    formula = formula.replace('∨', '|')
    formula = formula.replace('v', '|')  # Handle 'v' as disjunction
    
    # Replace proposition variables (A1, A2, etc. -> p1, p2, etc.)
    formula = re.sub(r'A(\d+)', r'p\1', formula)
    
    # Convert box operators: □i(φ) -> @_i [i] φ
    # Pattern matches □ followed by agent number and parenthesized formula
    def replace_box(match):
        agent = match.group(1)
        inner_formula = match.group(2)
        return f'[{agent}] ({inner_formula})'
    
    # Handle □i(...) patterns
    while re.search(r'□(\d+)\(([^)]+)\)', formula):
        formula = re.sub(r'□(\d+)\(([^)]+)\)', replace_box, formula)
    
    # Handle negated box operators: ~□i(...) 
    # This needs special handling to ensure proper placement
    # formula = re.sub(r'~@_(\d+) \[(\d+)\] ', r'@_\1 <\2> ~', formula)
    
    return formula


def convert_multiline_formula(formula_text):
    """
    Convert a multi-line modal logic formula to InToHyLo format.
    
    Args:
        formula_text: String containing the complete formula (possibly multi-line)
        
    Returns:
        String in InToHyLo format
    """
    # Join lines and clean up
    formula = ' '.join(formula_text.split())
    
    # Remove trailing conjunction if present
    formula = formula.rstrip('∧').rstrip('&').strip()
    
    return convert_to_intohylo(formula)


def convert_multiple_formulas(text):
    """
    Convert multiple modal logic formulas to InToHyLo format.
    Formulas are separated by newlines or semicolons.
    
    Args:
        text: String containing multiple formulas
        
    Returns:
        List of converted formulas
    """
    # Split by newlines first
    lines = text.strip().split('\n')
    
    formulas = []
    current_formula = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            if current_formula:
                # End of a formula
                formula_text = ' '.join(current_formula)
                formulas.append(formula_text)
                current_formula = []
            continue
        
        # Check if line ends with a conjunction/continuation
        if line.endswith('∧') or line.endswith('&') or line.endswith('∨') or line.endswith('|'):
            current_formula.append(line)
        else:
            # Check if this might be a continuation (starts with operator or parenthesis)
            if current_formula and (line.startswith('(') or line.startswith('¬') or line.startswith('~')):
                current_formula.append(line)
            else:
                # This is a new formula
                if current_formula:
                    formula_text = ' '.join(current_formula)
                    formulas.append(formula_text)
                    current_formula = []
                current_formula.append(line)
    
    # Don't forget the last formula
    if current_formula:
        formula_text = ' '.join(current_formula)
        formulas.append(formula_text)
    
    # Also try splitting by semicolons if no newline-separated formulas found
    if len(formulas) == 1 and ';' in text:
        formulas = [f.strip() for f in text.split(';') if f.strip()]
    
    # Convert each formula
    converted = []
    for formula in formulas:
        if formula:
            converted.append(convert_to_intohylo(formula))
    
    return converted


def main():
    """Main function with CLI argument parsing."""
    
    parser = argparse.ArgumentParser(
        description='Convert modal logic formulas to InToHyLo format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -f "□1(A4 v A3) ∧ ¬□1(A1)"
  %(prog)s -f "□1(A1 ∧ A2)" -o output.txt
  %(prog)s -i input.txt -o output.txt
  %(prog)s --interactive
        """
    )
    
    parser.add_argument('-f', '--formula', type=str,
                        help='Modal logic formula to convert')
    parser.add_argument('-i', '--input', type=str,
                        help='Input file containing modal logic formula')
    parser.add_argument('-o', '--output', type=str,
                        help='Output file for InToHyLo result')
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
    
    # Process formula from command line or file
    result = None
    results = []
    
    if args.formula:
        result = convert_to_intohylo(args.formula)
        results = [result]
        print(f"Input:  {args.formula}")
        print(f"Output: {result}")
    elif args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert multiple formulas
            results = convert_multiple_formulas(content)
            
            print(f"Converted {len(results)} formula(s) from: {args.input}")
            print()
            for i, converted in enumerate(results, 1):
                print(f"Formula {i}: {converted}")
            
            result = '\n'.join(results)
            
        except FileNotFoundError:
            print(f"Error: File '{args.input}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        return
    
    # Write to output file if specified
    if args.output and results:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                for converted in results:
                    f.write(converted + '\n')
            print(f"\nOutput written to: {args.output} ({len(results)} formula(s))")
        except Exception as e:
            print(f"Error writing to file: {e}")
            sys.exit(1)


def show_examples():
    """Display example conversions."""
    examples = [
        ("Example 1", "(□1(A4 v A3)) ∧ (¬□1(A1))"),
        ("Example 2", "□1(A1 ∧ A2) ∧ □2(A3 ∨ A4)"),
        ("Example 3", "□3(A5)"),
        ("Example 4", "¬□1(A1 ∨ A2)"),
    ]
    
    for title, formula in examples:
        print(f"{title}:")
        print(f"Input:  {formula}")
        print(f"Output: {convert_to_intohylo(formula)}")
        print()


def interactive_mode():
    """Run the converter in interactive mode."""
    print("Interactive Mode - Modal Logic to InToHyLo Converter")
    print("Enter a modal logic formula (or 'quit' to exit):")
    
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            if user_input.strip():
                result = convert_to_intohylo(user_input)
                print(f"InToHyLo: {result}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()