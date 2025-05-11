import sys
import time

class Clause:
    def __init__(self):
        self.symbols = {}

    def dimacs(self, literals, variable_map):
        self.symbols = {}
        for literal in literals:
            sign = 1 if literal > 0 else -1
            variable_index = abs(literal)
            if variable_index in variable_map:
                symbol = variable_map[variable_index]
                self.symbols[symbol] = sign
            else:
                raise ValueError(f"Literal {literal} refers to an undefined variable")

    def format(self):
        parts = []
        for var, sign in self.symbols.items():
            if sign == -1:
                parts.append("-" + var)
            else:
                parts.append(var)
        return " ".join(parts)

class SatInstance:
    def __init__(self):
        self.symbols = set()
        self.clauses = []

    def dimacs_file(self, file):
        self.symbols = set()
        self.clauses = []
        variable_map = {}

        with open(file, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("c"):
                    continue
                elif line.startswith("p cnf"):
                    parts = line.split()
                    if len(parts) == 4 and parts[0] == "p" and parts[1] == "cnf":
                        num_vars = int(parts[2])
                        for i in range(1, num_vars + 1):
                            variable_map[i] = f"x{i}"
                    else:
                        raise ValueError("Invalid DIMACS preamble")
                elif line:
                    literals = [int(l) for l in line.split() if l != '0']
                    if literals:
                        clause = Clause()
                        clause.dimacs(literals, variable_map)
                        self.clauses.append(clause)
                        for symbol in clause.symbols:
                            self.symbols.add(symbol)

        self.symbols = sorted(list(self.symbols), key=lambda s: int(s[1:])) if self.symbols else []

    def is_satisfied(self, assignment):
        for clause in self.clauses:
            satisfied = False
            for symbol, sign in clause.symbols.items():
                if symbol in assignment and assignment[symbol] == sign:
                    satisfied = True
                    break
            if not satisfied:
                return False
        return True

def convert_to_clause_list(instance):
    """
    Convert SatInstance.clauses (list of Clause objects)
    to list of frozensets of integers for dp()
    """
    symbol_to_int = {s: i + 1 for i, s in enumerate(instance.symbols)}
    clause_list = []

    for clause in instance.clauses:
        clause_lits = set()
        for symbol, sign in clause.symbols.items():
            lit = symbol_to_int[symbol] * sign
            clause_lits.add(lit)
        clause_list.append(frozenset(clause_lits))

    return clause_list

def dp(clauses):
    """
    Davis–Putnam algorithm.
    clauses: list of frozensets, e.g. [{1, -2}, {-1, 3}, {-2}]
    returns: True if SAT, False if UNSAT
    """
    if frozenset() in clauses:
        return False
    if not clauses:
        return True

    variables = set(abs(lit) for clause in clauses for lit in clause)
    if not variables:
        return True

    var = next(iter(variables))

    pos_clauses = [c for c in clauses if var in c]
    neg_clauses = [c for c in clauses if -var in c]
    rest_clauses = [c for c in clauses if var not in c and -var not in c]

    resolvents = []
    for c1 in pos_clauses:
        for c2 in neg_clauses:
            new_clause = (c1 - {var}) | (c2 - {-var})
            if not new_clause:
                return False
            resolvents.append(frozenset(new_clause))

    new_formula = rest_clauses + resolvents
    return dp(new_formula)

def main():
    if len(sys.argv) != 2:
        print("Usage: python your_script_name.py <dimacs_input_file>")
        sys.exit(1)

    input_filename = sys.argv[1]
    instance = SatInstance()
    try:
        instance.dimacs_file(input_filename)
        start_time = time.time()
        clause_list = convert_to_clause_list(instance)
        result = dp(clause_list)
        end_time = time.time()
        duration = end_time - start_time

        if result:
            print("Satisfiable")
        else:
            print("Unsatisfiable")
        print(f"Time: {duration:.4f}s")

    except FileNotFoundError:
        print(f"Error: Input file '{input_filename}' not found.")
    except ValueError as e:
        print(f"Error parsing DIMACS file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()