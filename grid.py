from __future__ import annotations

import csv
from pathlib import Path

import colorama

colorama.init(autoreset=True)
GRIDS_PATH = Path(__file__).resolve().parent / "grids"
GRID_SIZE = 5
VALID_CHARS = "ABCDE12345 "


class Grid:
    def __init__(self, grid_id, load_solution=False):
        file_name = str(grid_id).zfill(2) + ".csv"
        self.cells = self.load_file(file_name)
        if load_solution:
            self.solution_cells = self.load_file(file_name.replace(".csv", "_solution.csv"))
        self.move_count = 0
        self.solved_count = 0
        self.solved_values = Grid.SolvedValues()
        self.__scan_solved_cells()

    # TODO: decorator to validate grid
    #   5 * 5
    #   2 chars per cell
    #   supported chars:
    #       1st pos: ABCDE_
    #       2nd pos: 12345_
    @classmethod
    def load_file(cls, grid_file_name):
        grid_path = GRIDS_PATH / grid_file_name
        try:
            with open(grid_path, newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))
                return cls.init_cells(rows)
        except FileNotFoundError:
            raise SystemExit(f"Error: grid_id '{grid_path}' doesn't exist.")

    @staticmethod
    def init_cells(matrix):
        cells = []
        for row in matrix:
            for cell in row:
                letter = cell[0] if cell[0] in "ABCDE" else None
                digit = cell[1] if cell[1] in "12345" else None
                cells.append(Grid.Cell(letter, digit))
        return cells

    def __scan_solved_cells(self):
        for cell in self.cells:
            if cell.is_solved():
                self.__save_solved_value(cell)

    class Cell:
        def __init__(self, letter, digit):
            self.letter = letter
            self.digit = digit

        def is_solved(self):
            return self.letter is not None and self.digit is not None

        def set_char(self, char):
            if char.isalpha():
                self.letter = char
            else:
                self.digit = char

        def __contains__(self, char):
            if char.isalpha():
                return char == self.letter
            return char == self.digit

        def __str__(self):
            return (self.letter if self.letter is not None else " ") \
                + (self.digit if self.digit is not None else " ")

    class Value(Cell):
        @classmethod
        def from_cell(cls, cell, char):
            letter = char if char.isalpha() else cell.letter
            digit = char if not char.isalpha() else cell.digit
            return cls(letter, digit)

    def get_row(self, index):
        return self.cells[index * GRID_SIZE: (index + 1) * GRID_SIZE]

    def get_column(self, index):
        return [self.cells[row * GRID_SIZE + index] for row in range(GRID_SIZE)]

    @staticmethod
    def __char_in_cells(char, cells):
        for cell in cells:
            if char in cell:
                return True
        return False

    def char_in_row(self, char, index):
        return self.__char_in_cells(char, self.get_row(index))

    def char_in_column(self, char, index):
        return self.__char_in_cells(char, self.get_column(index))

    def set_char(self, row, column, char, display=False):
        self.__validate_char(char)
        self.__validate_is_not_occupied(row, column, char)
        if self.solution_cells is not None:
            self.__validate_move(row, column, char)

        cell = self.get_cell(row, column)
        cell.set_char(char)
        if cell.is_solved():
            self.__save_solved_value(cell)
        self.move_count += 1
        if display:
            self.display(row, column, char)
            print(self.move_count, "moves")

    @staticmethod
    def __validate_char(char):
        if len(char) != 1 or char not in VALID_CHARS:
            raise ValueError(f"Invalid char [char: '{char}']")

    def __validate_is_not_occupied(self, row, column, char):
        cell = self.get_cell(row, column)
        if self.__is_occupied(cell, char):
            raise ValueError(
                f"Cell is already occupied [y='{row}', x='{column}', cell='{cell}', char='{char}']")

    def get_cell(self, row, column):
        return self.cells[row * GRID_SIZE + column]

    @staticmethod
    def __is_occupied(cell, char):
        if char.isalpha():
            return cell.letter is not None
        return cell.digit is not None

    def __validate_move(self, row, column, char):
        solution_cell = self.__get_solution_cell(row, column)
        if char.isalpha():
            expected_char = solution_cell.letter
        else:
            expected_char = solution_cell.digit
        if char != expected_char:
            raise ValueError(
                f"Wrong value inserted [y='{row}', x='{column}', insert='{char}', expected='{expected_char}']"
            )

    def __get_solution_cell(self, row, column):
        return self.solution_cells[row * GRID_SIZE + column]

    def is_solved_value(self, value: Grid.Value):
        if not value.is_solved():
            return False
        return value.digit in self.solved_values.letters[value.letter]

    def __save_solved_value(self, cell):
        self.solved_values.letters[cell.letter].append(cell.digit)
        self.solved_values.digits[cell.digit].append(cell.letter)
        self.solved_count += 1

    def is_taken(self, row, column, char):
        cell = self.get_cell(row, column)
        if char.isalpha():
            return cell.letter is not None
        return cell.digit is not None

    def display(self, accent_row=None, accent_column=None, accent_char=None):
        def row_separator():
            print(GRID_SIZE * "----" + (GRID_SIZE + 1) * "-")

        def print_accent(s, y, x, char, end="\n"):
            if y == accent_row and x == accent_column:
                s = s.replace(char, colorama.Fore.GREEN + char + colorama.Style.RESET_ALL)
            print(s, end=end)

        row_separator()
        for y in range(GRID_SIZE):
            print("|", end="")
            for x in range(GRID_SIZE):
                print_accent(f" {str(self.get_cell(y, x))} |", y, x, accent_char, end="")
            print()
            row_separator()

    def get_unsolved_associations(self, row, column):
        cell = self.get_cell(row, column)
        char = str(cell).strip()
        if len(char) != 1:
            return set()
        return self.solved_values.get_unsolved_associations(char)

    def is_solved(self):
        return self.solved_count == GRID_SIZE ** 2

    class SolvedValues:
        # TODO: avoir des références à des cells
        def __init__(self):
            self.letters = {}
            for letter in "ABCDE":
                self.letters[letter] = []
            self.digits = {}
            for digit in "12345":
                self.digits[digit] = []

        def __getitem__(self, char):
            if char.isalpha():
                return self.letters[char]
            return self.digits[char]

        def get_unsolved_associations(self, char):
            if char.isalpha():
                return set(self.letters[char]) ^ set("12345")
            return set(self.digits[char]) ^ set("ABCDE")

        def __str__(self):
            res = "Solved values:\n"
            for letter in "ABCDE":
                res += "| "
                for digit in "12345":
                    if digit in self.letters[letter]:
                        res += letter + digit
                    else:
                        res += "  "
                    res += " | "
                res += "\n"
            return res
