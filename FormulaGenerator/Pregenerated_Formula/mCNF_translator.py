import re
import argparse
import sys

class FormulaTranslator:
    def __init__(self):
        self.tokens = []
        self.pos = 0
    
    def tokenize(self, formula):
        """Tokenize the input formula"""
        # Remove extra whitespace and split by parentheses and spaces
        formula = formula.strip()
        tokens = []
        current = ""
        
        for char in formula:
            if char in '()':
                if current.strip():
                    tokens.append(current.strip())
                    current = ""
                tokens.append(char)
            elif char.isspace():
                if current.strip():
                    tokens.append(current.strip())
                    current = ""
            else:
                current += char
        
        if current.strip():
            tokens.append(current.strip())
        
        return tokens
    
    def parse(self, tokens):
        """Parse tokens into InToHyLo format"""
        self.tokens = tokens
        self.pos = 0
        return self.parse_expression()
    
    def parse_expression(self):
        """Parse a single expression"""
        if self.pos >= len(self.tokens):
            raise ValueError("Unexpected end of formula")
        
        token = self.tokens[self.pos]
        
        # Handle opening parenthesis
        if token == '(':
            self.pos += 1
            return self.parse_compound()
        else:
            # Atomic proposition
            self.pos += 1
            return token.replace('C', 'p')
    
    def parse_compound(self):
        """Parse compound expressions (AND, OR, NOT, ALL)"""
        if self.pos >= len(self.tokens):
            raise ValueError("Unexpected end of formula")
        
        operator = self.tokens[self.pos]
        self.pos += 1
        
        if operator == 'NOT':
            # Negation: ~phi
            arg = self.parse_expression()
            if self.tokens[self.pos] != ')':
                raise ValueError(f"Expected ')', got '{self.tokens[self.pos]}'")
            self.pos += 1
            return f"~({arg})"
        
        elif operator == 'AND':
            # Conjunction: phi & psi & ...
            args = []
            while self.tokens[self.pos] != ')':
                args.append(self.parse_expression())
            self.pos += 1  # skip ')'
            
            if len(args) == 1:
                return args[0]
            result = args[0]
            for arg in args[1:]:
                result = f"({result} & {arg})"
            return result
        
        elif operator == 'OR':
            # Disjunction: phi | psi | ...
            args = []
            while self.tokens[self.pos] != ')':
                args.append(self.parse_expression())
            self.pos += 1  # skip ')'
            
            if len(args) == 1:
                return args[0]
            result = args[0]
            for arg in args[1:]:
                result = f"({result} | {arg})"
            return result
        
        elif operator == 'ALL':
            # Box modality: [R]phi
            relation = self.tokens[self.pos]
            self.pos += 1
            formula = self.parse_expression()
            if self.tokens[self.pos] != ')':
                raise ValueError(f"Expected ')', got '{self.tokens[self.pos]}'")
            self.pos += 1
            return f"[{relation.lower()}]({formula})"
        
        else:
            raise ValueError(f"Unknown operator: {operator}")
    
    def translate(self, formula):
        """Main translation function"""
        tokens = self.tokenize(formula)
        result = self.parse(tokens)
        return result


def translate_to_intohylo(formula):
    """
    Translate a formula from the given format to InToHyLo format.
    
    Format conversion:
    - AND -> &
    - OR -> |
    - NOT -> ~
    - ALL R phi -> [R](phi)
    - Atomic propositions remain the same
    
    Args:
        formula: String containing the formula in the input format
    
    Returns:
        String containing the formula in InToHyLo format
    """
    translator = FormulaTranslator()
    return translator.translate(formula)


def parse_multiple_formulas(text, separator):
    """
    Parse multiple formulas from text.
    Formulas can be separated by blank lines or each on a single line.
    Multi-line formulas are supported if they're separated by blank lines.
    """
    formulas = []
    current_formula = []
    
    lines = text.split(separator)
    
    for i in range(len(lines)):
        lines[i] = lines[i].strip('\n')
        
    
    # # Don't forget the last formula if file doesn't end with blank line
    # if current_formula:
    #     formulas.append(' '.join(current_formula))
    
    return lines


def process_single_formula(formula, args):
    """Process a single formula"""
    try:
        result = translate_to_intohylo(formula)
        
        # Display or save output
        if not args.quiet:
            print("Input formula:")
            print(formula)
            print("\nInToHyLo format:")
        
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    f.write(result)
                if not args.quiet:
                    print(f"(Output written to {args.output})")
                else:
                    print(result)
            except IOError as e:
                print(f"Error writing to file: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print(result)
            
    except Exception as e:
        print(f"Error translating formula: {e}", file=sys.stderr)
        sys.exit(1)


def process_multiple_formulas(formulas, args):
    """Process multiple formulas"""
    if not formulas:
        print("Error: No formulas found", file=sys.stderr)
        sys.exit(1)
    
    results = []
    errors = []
    
    for i, formula in enumerate(formulas, 1):
        try:
            result = translate_to_intohylo(formula)
            results.append((formula, result, None))
        except Exception as e:
            results.append((formula, None, str(e)))
            errors.append((i, str(e)))
    
    # Output results
    if args.output:
        # Write to file
        try:
            with open(args.output, 'w') as f:
                for i, (original, result, error) in enumerate(results, 1):
                    if error:
                        f.write(f"# Formula {i}: ERROR - {error}\n")
                        f.write(f"# Input: {original}\n")
                    else:
                        if not args.quiet:
                            f.write(f"# Formula {i}\n")
                            f.write(f"# Input: {original}\n")
                        f.write(result + "\n")
                    
                    if i < len(results):
                        f.write("\n")
            
            if not args.quiet:
                print(f"Processed {len(results)} formulas")
                print(f"Output written to {args.output}")
                if errors:
                    print(f"\nErrors in {len(errors)} formula(s):")
                    for num, err in errors:
                        print(f"  Formula {num}: {err}")
        except IOError as e:
            print(f"Error writing to file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Print to stdout
        for i, (original, result, error) in enumerate(results, 1):
            if i > 1:
                print(f"\n{args.separator}\n")
            
            if not args.quiet:
                print(f"Formula {i}:")
                print(f"Input: {original}")
                print()
            
            if error:
                print(f"ERROR: {error}")
            else:
                if not args.quiet:
                    print("InToHyLo format:")
                print(result)


def main():
    """Main function with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description='Translate formulas to InToHyLo format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Translate a formula directly
  python script.py -f "(AND C1 C2)"
  
  # Read from a file
  python script.py -i input.txt
  
  # Process multiple formulas from a file
  python script.py -i formulas.txt -m
  
  # Write output to a file
  python script.py -f "(OR C1 C2)" -o output.txt
  
  # Process multiple formulas with custom separator
  python script.py -i formulas.txt -m -s "===" -o output.txt
  
  # Read from stdin
  echo "(NOT C1)" | python script.py
  
  # Run test examples
  python script.py --test

Translation rules:
  AND -> &  (conjunction)
  OR  -> |  (disjunction)
  NOT -> ~  (negation)
  ALL R phi -> [R](phi)  (box modality)
        """
    )
    
    parser.add_argument('-f', '--formula', 
                        type=str,
                        help='Formula string to translate')
    
    parser.add_argument('-i', '--input',
                        type=str,
                        help='Input file containing the formula')
    
    parser.add_argument('-o', '--output',
                        type=str,
                        help='Output file for the translated formula')
    
    parser.add_argument('--test',
                        action='store_true',
                        help='Run test examples')
    
    parser.add_argument('-q', '--quiet',
                        action='store_true',
                        help='Suppress input echo (only output result)')
    
    parser.add_argument('-m', '--multiple',
                        action='store_true',
                        help='Process multiple formulas (one per line or separated by blank lines)')
    
    parser.add_argument('-s', '--separator',
                        type=str,
                        default='---',
                        help='Separator between multiple formula outputs (default: ---)')
    
    args = parser.parse_args()
    
    # Run tests if requested
    if args.test:
        run_tests()
        return
    
    # Get input formula
    formula = None
    
    if args.formula:
        formula = args.formula
    elif args.input:
        try:
            with open(args.input, 'r') as f:
                formula = f.read().strip()
        except FileNotFoundError:
            print(f"Error: File '{args.input}' not found", file=sys.stderr)
            sys.exit(1)
        except IOError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin if no formula or file provided
        if not sys.stdin.isatty():
            formula = sys.stdin.read().strip()
        else:
            parser.print_help()
            sys.exit(1)
    
    if not formula:
        print("Error: No formula provided", file=sys.stderr)
        sys.exit(1)
    
    # Handle multiple formulas
    if args.multiple:
        formulas = parse_multiple_formulas(formula, args.separator)
        process_multiple_formulas(formulas, args)
    else:
        # Single formula mode
        process_single_formula(formula, args)


def run_tests():
    """Run test examples"""
    print("="*60)
    print("Running test examples")
    print("="*60)
    
    # Test with the provided example
    test_formula = """(AND (OR  (NOT (ALL R1 (OR  (NOT C1) C4 C5) ))
    (ALL R1 (OR  (NOT C1) C2 C3) )
    (NOT (ALL R1 (OR  (NOT C2) (NOT C3) C5) )) )"""
    
    print("\n1. Complex example:")
    print("Input:")
    print(test_formula)
    print("\nOutput:")
    result = translate_to_intohylo(test_formula)
    print(result)
    
    # Additional test cases
    print("\n" + "="*60)
    print("2. Additional test cases:")
    print("="*60)
    
    test_cases = [
        "(NOT C1)",
        "(AND C1 C2)",
        "(OR C1 C2 C3)",
        "(ALL R1 C1)",
        "(AND (ALL R1 C1) (NOT C2))",
        "(ALL R1 (OR (NOT C1) C2))",
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Input:  {test}")
        print(f"   Output: {translate_to_intohylo(test)}")


# Example usage
if __name__ == "__main__":
    main()