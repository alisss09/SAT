import sys
import time

class Clause:
    def __init__(self):
        self.symbols = {}

    def from_dimacs(self, literals, variable_map):
        self.symbols = {}
        for literal in literals:
            sign = 1 if literal > 0 else -1
            variable_index = abs(literal)
            if variable_index in variable_map:
                symbol = variable_map[variable_index]
                self.symbols[symbol] = sign
            else:
                raise ValueError(f"Literal {literal} refers to an undefined variable")

    def __str__(self):
        tokens = []
        for symbol, sign in self.symbols.items():
            token = ""
            if sign == -1:
                token += "-"
            token += symbol
            tokens.append(token)
        return " ".join(tokens)

class SatInstance:
    def __init__(self):
        self.symbols = set()
        self.clauses = []

    def from_dimacs_file(self, filename):
        self.symbols = set()
        self.clauses = []
        variable_map = {}

        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("c"):
                    continue  # Skip comments
                elif line.startswith("p cnf"):
                    parts = line.split()
                    if len(parts) == 4 and parts[0] == "p" and parts[1] == "cnf":
                        num_vars = int(parts[2])
                        # Initialize variable map based on the declared number of variables
                        for i in range(1, num_vars + 1):
                            variable_map[i] = f"x{i}"
                    else:
                        raise ValueError("Invalid DIMACS preamble")
                elif line:
                    literals = [int(l) for l in line.split() if l != '0']
                    if literals:
                        clause = Clause()
                        clause.from_dimacs(literals, variable_map)
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

    def find_unit_clause(self):
        for clause in self.clauses:
            if len(clause.symbols) == 1:
                symbol, sign = next(iter(clause.symbols.items()))
                return {symbol: sign}
        return None

    def simplify(self, assignment):
        new_clauses = []
        for clause in self.clauses:
            satisfied = False
            new_symbols = {}
            for symbol, sign in clause.symbols.items():
                if symbol in assignment:
                    if assignment[symbol] == sign:
                        satisfied = True
                        break
                else:
                    new_symbols[symbol] = sign
            if not satisfied:
                if not new_symbols:
                    return None  # Found an empty clause, so it's unsatisfiable
                new_clause = Clause()
                new_clause.symbols = new_symbols
                new_clauses.append(new_clause)
        new_instance = SatInstance()
        new_instance.clauses = new_clauses
        new_instance.symbols = sorted(list(set().union(*(c.symbols for c in new_clauses))), key=lambda s: int(s[1:])) if new_clauses else []
        return new_instance

def solve_dpll(instance, assignment=None):
    if assignment is None:
        assignment = {}

    unit_clause = instance.find_unit_clause()
    while unit_clause:
        symbol, sign = next(iter(unit_clause.items()))
        if symbol in assignment and assignment[symbol] != sign:
            return None  # Conflict found
        assignment[symbol] = sign
        instance = instance.simplify({symbol: sign})
        if instance is None:
            return None  # Unsatisfiable
        if not instance.clauses:
            return assignment  # All clauses satisfied
        unit_clause = instance.find_unit_clause()

    if not instance.clauses:
        return assignment  # All clauses satisfied

    unassigned_symbol = next((s for s in instance.symbols if s not in assignment), None)
    if unassigned_symbol is None:
        return assignment

    assignment_true = assignment.copy()
    assignment_true[unassigned_symbol] = 1
    result_true = solve_dpll(instance.simplify({unassigned_symbol: 1}), assignment_true)
    if result_true:
        return result_true

    assignment_false = assignment.copy()
    assignment_false[unassigned_symbol] = -1
    result_false = solve_dpll(instance.simplify({unassigned_symbol: -1}), assignment_false)
    return result_false

def main():
    if len(sys.argv) != 2:
        print("Usage: python your_script_name.py <dimacs_input_file>")
        sys.exit(1)

    input_filename = sys.argv[1]
    instance = SatInstance()
    try:
        instance.from_dimacs_file(input_filename)
        start_time = time.time()
        assignment = solve_dpll(instance)  # Or solve_sat_dp for the other version
        end_time = time.time()
        duration = end_time - start_time

        if assignment:
            print("Satisfiable", end=" ")
        else:
            print("Unsatisfiable", end="")
        print(f"\nTime: {duration:.4f}s")

    except FileNotFoundError:
        print(f"Error: Input file '{input_filename}' not found.")
    except ValueError as e:
        print(f"Error parsing DIMACS file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()