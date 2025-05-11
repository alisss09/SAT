import sys
import time

def dimacs(file):
    """Parses a DIMACS CNF file and returns a list of clauses as frozensets of integers."""
    clauses = []
    file = "input.cnf"
    with open(file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("c") or line == "" or line.startswith("p"):
                continue
            literals = [int(lit) for lit in line.split() if lit != '0']
            if literals:
                clauses.append(frozenset(sorted(literals)))
    return clauses

def resolve(c1, c2):
    for lit in c1:
        if -lit in c2:
            return (c1 - {lit}) | (c2 - {-lit})
    return None

def resolution(clauses):
    """Performs the resolution algorithm. Returns 'UNSAT' if contradiction is found, otherwise 'SAT'."""
    known = set(clauses)
    while True:
        new_clauses = set()
        known_list = list(known)

        for i in range(len(known_list)):
            for j in range(i + 1, len(known_list)):
                c1, c2 = known_list[i], known_list[j]
                resolvent = resolve(c1, c2)
                if resolvent is not None:
                    if not resolvent:
                        return "Unsatisfiable"
                    if resolvent not in known:
                        new_clauses.add(resolvent)

        if not new_clauses:
            return "Satisfiable"

        known.update(new_clauses)

def main():
    if len(sys.argv) != 2:
        print("Usage: python simple_resolution.py <dimacs_input_file>")
        sys.exit(1)

    try:
        filename = sys.argv[1]
        clauses = dimacs(filename)

        start = time.time()
        result = resolution(clauses)
        end = time.time()

        print(result)
        print(f"Time: {end - start:.4f}s")

    except FileNotFoundError:
        print(f"File not found: {sys.argv[1]}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()