assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B):
    return [s+t for s in A for t in B]

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# include 2 main diagonals as units to solve the diagonal sudoku problem
diagonal_units = [['A1','B2', 'C3','D4','E5', 'F6','G7','H8', 'I9'], ['A9','B8', 'C7','D6','E5', 'F4','G3','H2', 'I1']]

unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    def find_naked_twins(values, arr):
        """this is a private function to find naked twins if we have more than 2"""
        found_twins = []
        n = len(arr)
        for i in range(n):
            for j in range(1, n):
                if i == j:
                    continue
                if values[arr[i]] == values[arr[j]]:
                    found_twins.append(arr[i])
                    found_twins.append(arr[j])
        return found_twins if len(found_twins) > 1 else False

    for unit in unitlist:
        twins = []
        # get list of boxes with just 2 values
        twos = [box for box in unit if len(values[box]) == 2]
        if len(twos) < 2:
            continue
        if len(twos) == 2 and values[twos[0]] != values[twos[1]]:
            continue
        if len(twos) == 2 and values[twos[0]] == values[twos[1]]:
            twins.append(twos)
        else:
            found_twins = find_naked_twins(values, twos)
            if found_twins:
                twins.append(found_twins)
        # flatten the list of naked twins
        found_twins_boxes = [box for twin in twins for box in twin] 
        # get non naked twin pairs
        other_unit = [box for box in unit if box not in found_twins_boxes]
        # get list of values to eliminate from pairs
        values_to_eliminate = "".join([values[twin[0]] for twin in twins])
        for value in values_to_eliminate:
            for box in other_unit:
                values = assign_value(values, box, values[box].replace(value, ''))
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    """
    values = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            values.append(all_digits)
        elif c in all_digits:
            values.append(c)
    assert len(values) == 81
    return dict(zip(boxes, values))

def display(values):
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    for box, value in values.items():
        if len(value) == 1:
            for peer in peers[box]:
                values = assign_value(values, peer, values[peer].replace(value, ''))
    return values

def only_choice(values):
    for unit in unitlist:
        for digit in '123456789':
            choice_boxes = [box for box in unit if digit in values[box]]
            if len(choice_boxes) == 1:
                values[choice_boxes[0]] = digit
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in boxes if len(values[box]) == 1])
        values = naked_twins(only_choice(eliminate(values)))
        solved_values_after = len([box for box in boxes if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in boxes if len(values[box]) == 0]):
            return False
    return values

def search(values):
    #reduce the puzzle
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[box])==1 for box in boxes):
        return values

    # Choose a box with fewest possibilities
    n, fpBox = min((len(values[box]), box) for box in values if len(values[box]) > 1)

    for value in values[fpBox]:
        sudoku = values.copy()
        sudoku[fpBox] = value
        resolved = search(sudoku)
        if resolved:
            return resolved

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    sudoku = grid_values(grid)
    return search(sudoku)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
