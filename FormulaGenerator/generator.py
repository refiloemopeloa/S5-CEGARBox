#!/usr/bin/env python3
"""
3CNF Random Formula Generator
Implementation of the algorithm from Giunchiglia et al., 2000
"""

import random
import argparse
import json
import sys


def rnd_sign():
    """Select randomly either positive or negative sign with equal probability."""
    return random.random() < 0.5


def rnd_propositional_atom(N):
    """Select randomly a propositional atom from A1, ..., AN."""
    return f"A{random.randint(1, N)}"


def rnd_box(m):
    """Select randomly an indexed box from □1, ..., □m."""
    return f"□{random.randint(1, m)}"


def rnd_length(d, C):
    """Select randomly the clause length according to the d+1-th distribution in C."""
    if d >= len(C):
        return 3  # Default to 3 if no distribution available
    
    dist = C[d]
    total = sum(dist)
    
    if total == 0:
        return len(dist)
    
    r = random.random() * total
    cumulative = 0
    
    for i, val in enumerate(dist):
        cumulative += val
        if r <= cumulative:
            return i + 1
    
    return len(dist)


def rnd_propnum(d, p, K):
    """Select randomly the number of propositional atoms per clause P."""
    if d >= len(p):
        return 0
    
    depth_dist = p[d]
    if K - 1 >= len(depth_dist):
        return 0
    
    length_dist = depth_dist[K - 1]
    total = sum(length_dist)
    
    if total == 0:
        return 0
    
    r = random.random() * total
    cumulative = 0
    
    for i, val in enumerate(length_dist):
        cumulative += val
        if r <= cumulative:
            return i
    
    return 0


def rnd_atom(d, m, N, p, C):
    """Generate a random atom at depth d."""
    if d == 0:
        return rnd_propositional_atom(N)
    else:
        box = rnd_box(m)
        clause = rnd_clause(d - 1, m, N, p, C)
        return f"{box}({clause})"


def no_repeated_atoms_in(clause):
    """Check if the clause contains no repeated atoms."""
    atoms = set()
    for literal in clause:
        # Extract the atom (remove negation if present)
        atom = literal[1:] if literal.startswith('¬') else literal
        if atom in atoms:
            return False
        atoms.add(atom)
    return True


def rnd_clause(d, m, N, p, C):
    """Generate a random clause at depth d."""
    max_attempts = 100
    attempts = 0
    
    while attempts < max_attempts:
        K = rnd_length(d, C)
        P = rnd_propnum(d, p, K)
        
        clause = []
        
        # Generate P propositional literals
        for j in range(P):
            atom = rnd_propositional_atom(N)
            sign = rnd_sign()
            literal = f"¬{atom}" if sign else atom
            clause.append(literal)
        
        # Generate K-P modal literals
        for j in range(P, K):
            atom = rnd_atom(d, m, N, p, C)
            sign = rnd_sign()
            literal = f"¬{atom}" if sign else atom
            clause.append(literal)
        
        if no_repeated_atoms_in(clause):
            return ' ∨ '.join(sorted(clause))
        
        attempts += 1
    
    # If we can't generate a valid clause, return what we have
    return ' ∨ '.join(sorted(clause))


def is_new(clause, existing_clauses):
    """Check if the clause is not already in the list."""
    return clause not in existing_clauses


def rnd_CNF(d, m, L, N, p, C):
    """Generate L distinct random clauses and form their conjunction."""
    clauses = []
    max_attempts = L * 10
    attempts = 0
    
    while len(clauses) < L and attempts < max_attempts:
        clause = rnd_clause(d, m, N, p, C)
        if is_new(clause, clauses):
            clauses.append(clause)
        attempts += 1
    
    return clauses


def format_formula(clauses):
    """Format the formula for display."""
    if not clauses:
        return ""
    
    lines = []
    for i, clause in enumerate(clauses):
        connector = ' ∧' if i < len(clauses) - 1 else '.'
        lines.append(f"  ({clause}){connector}")
    
    return '\n'.join(lines)


def parse_distribution(dist_str):
    """Parse a distribution string into a nested list."""
    try:
        return json.loads(dist_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid distribution format: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate random 3CNF modal logic formulas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default parameters
  python cnf_generator.py
  
  # Custom parameters
  python cnf_generator.py -d 2 -L 4 -N 4 -m 1
  
  # With custom distributions
  python cnf_generator.py -C "[[0,2,2],[2,4],[6]]" -p "[[],[0,2,0],[0,2,0,0]]"
  
  # Save to file
  python cnf_generator.py -o formula.txt
  
  # Generate multiple formulas
  python cnf_generator.py --count 5

Notation:
  A₁, A₂, ... = propositional variables
  □₁, □₂, ... = modal box operators
  ¬ = negation
  ∨ = disjunction (OR)
  ∧ = conjunction (AND)
        """
    )
    
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
    parser.add_argument('-p', '--prop-dist', type=str, default='[[[],[0,2,0],[0,2,0,0]],[[2,0],[0,4,0]]]',
                        help='Propositional/modal rate distribution (default: [[[],[0,2,0],[0,2,0,0]],[[2,0],[0,4,0]]])')
    parser.add_argument('-o', '--output', type=str,
                        help='Output file (default: print to stdout)')
    parser.add_argument('--count', type=int, default=1,
                        help='Number of formulas to generate (default: 1)')
    parser.add_argument('--seed', type=int,
                        help='Random seed for reproducibility')
    parser.add_argument('--verbose', action='store_true',
                        help='Print parameter information')
    
    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
    
    # Parse distributions
    try:
        C = parse_distribution(args.clause_dist)
        p = parse_distribution(args.prop_dist)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate parameters
    if args.depth < 0:
        print("Error: depth must be non-negative", file=sys.stderr)
        sys.exit(1)
    if args.clauses < 1:
        print("Error: number of clauses must be at least 1", file=sys.stderr)
        sys.exit(1)
    if args.variables < 1:
        print("Error: number of variables must be at least 1", file=sys.stderr)
        sys.exit(1)
    if args.boxes < 1:
        print("Error: number of boxes must be at least 1", file=sys.stderr)
        sys.exit(1)
    
    # Print parameters if verbose
    if args.verbose:
        print("Parameters:")
        print(f"  Modal depth (d): {args.depth}")
        print(f"  Number of clauses (L): {args.clauses}")
        print(f"  Propositional variables (N): {args.variables}")
        print(f"  Box symbols (m): {args.boxes}")
        print(f"  Clause distribution (C): {C}")
        print(f"  Prop/modal distribution (p): {p}")
        if args.seed is not None:
            print(f"  Random seed: {args.seed}")
        print()
    
    # Generate formulas
    output_lines = []
    
    for i in range(args.count):
        if args.count > 1:
            output_lines.append(f"=== Formula {i + 1} ===")
        
        clauses = rnd_CNF(args.depth, args.boxes, args.clauses, args.variables, p, C)
        formula = format_formula(clauses)
        output_lines.append(formula)
        
        if i < args.count - 1:
            output_lines.append("")
    
    output_text = '\n'.join(output_lines)
    
    # Write output
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_text)
            print(f"Formula saved to {args.output}")
        except IOError as e:
            print(f"Error writing to file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_text)


if __name__ == '__main__':
    main()