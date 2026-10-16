from __future__ import annotations

import csv
import math
import re
from pathlib import Path

import colorama

import util

colorama.init(autoreset=True)
GRIDS_PATH = Path(__file__).resolve().parent / "grids"
GRID_SIZE = 5
VALID_CHARS = "ABCDE12345 "
CELL_REGEX = r"^([A-Z]*)([0-9]*)$"


class Grid:
    def __init__(self, grid_id, load_solution=False):
        file_name = str(grid_id).zfill(2) + ".csv"
        self.cells = self.load_file(file_name)
        if load_solution:
            self.solution_cells = self.load_file(file_name.replace(".csv", "_solution.csv"))
        grid_size = int(math.sqrt(len(self.cells)))
        self.valid_letters, self.valid_digits = self.__init_valid_chars(grid_size=grid_size)
        self.valid_chars = self.valid_letters + self.valid_digits
        self.move_count = 0
        self.solved_count = 0
        self.solved_values = Grid.SolvedValues(self.valid_letters, self.valid_digits)
        # TODO: conversion vers Cell qui supportent plusieurs lettres et chiffres
        #   Rendu à SolvedCells (Renommer pour solvedCellsGrid ?)
        self.__scan_solved_cells()
        self.cells_per_char = self.__init_cells_per_char(self.cells)

    @classmethod
    def load_file(cls, grid_file_name):
        grid_path = GRIDS_PATH / grid_file_name
        try:
            with open(grid_path, newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))
                cls.validate_grid(grid=rows)
                return cls.init_cells(rows)
        except FileNotFoundError:
            raise SystemExit(f"Error: grid_id '{grid_path}' doesn't exist.")

    @classmethod
    def validate_grid(cls, grid):
        row_count = len(grid)
        if row_count in [0, 2, 6]:
            raise ValueError(f"Invalid grid dimension [size='{row_count}']")

        for row_index, row in enumerate(grid):
            column_count = len(row)
            if column_count != row_count:
                raise ValueError(
                    f"Inconsistent grid dimensions [row_count='{row_count}', column_count for row {row_index}='{column_count}']")
            for column_index, cell_value in enumerate(row):
                cls.validate_cell_value(cell_value, grid_size=row_count)

    @classmethod
    def validate_cell_value(cls, cell_value, grid_size):
        value = cls.parse_value(cell_value)
        if value.letter:
            letter_decimal = util.alphabet_to_decimal(value.letter)
            if letter_decimal > grid_size or letter_decimal < 1:
                raise ValueError(
                    f"Letter value out of bounds [letter='{value.letter}', decimal_value='{letter_decimal}', grid_size={grid_size}]")
        if value.digit:
            digit_int = int(value.digit)
            if digit_int > grid_size or digit_int < 1:
                raise ValueError(
                    f"Digit value out of bounds [digit='{value.digit}', grid_size={grid_size}]")

    @classmethod
    def init_cells(cls, matrix):
        cells = []
        for row_index, row in enumerate(matrix):
            for column_index, cell_value in enumerate(row):
                value = cls.parse_value(cell_value)
                cell = value.to_cell(row_index, column_index)
                cells.append(cell)
        return cells

    @staticmethod
    def parse_value(cell_value) -> Grid.Value:
        match = re.search(CELL_REGEX, cell_value)
        if not match:
            raise ValueError(
                f"Invalid cell value. A cell must contain optional capital letters followed by optional digits [cell_value='{cell_value}']")
        groups = match.groups()
        return Grid.Value(
            letter=groups[0] or None,
            digit=groups[1] or None
        )

    @staticmethod
    def __init_valid_chars(grid_size):
        valid_letters = []
        valid_digits = []
        for i in range(1, grid_size + 1):
            valid_digits.append(str(i))
            letter = util.decimal_to_alphabet(i)
            valid_letters.append(letter)
        return valid_letters, valid_digits

    def __scan_solved_cells(self):
        for cell in self.cells:
            if cell.is_solved():
                self.__save_solved_value(cell)

    # FIXME: toutes les loops de chars devraient utiliser la taille de la grid
    def __init_cells_per_char(self, cells):
        cells_per_char = {}
        for char in self.valid_chars:
            cells_per_char[char] = []
        for cell in cells:
            if cell.letter is not None:
                cells_per_char[cell.letter].append(cell)
            if cell.digit is not None:
                cells_per_char[cell.digit].append(cell)
        return cells_per_char

    class Value:
        def __init__(self, letter, digit):
            self.letter = letter
            self.digit = digit if digit is not None else None

        @classmethod
        def from_value(cls, value: Grid.Value, char):
            letter = char if char.isalpha() else value.letter
            digit = char if not char.isalpha() else value.digit
            return cls(letter, digit)

        def to_cell(self, row_index, column_index):
            return Grid.Cell(self.letter, self.digit, row_index, column_index)

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
            return f"{self.letter if self.letter is not None else ' '}{self.digit if self.digit is not None else ' '}"

    class Cell(Value):
        def __init__(self, letter, digit, row, column):
            super().__init__(letter, digit)
            self.row = row
            self.column = column

        def __str__(self):
            return self.to_str(True)

        def to_str(self, coordinates: bool) -> str:
            return super().__str__() + (f" ({self.row}, {self.column})" if coordinates else "")

    def get_cells(self, char: str) -> Grid.Cell:
        return self.cells_per_char[char]

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

        cell = self.get_cell(row, column)
        cell.set_char(char)

        if self.solution_cells is not None:
            self.__validate_move(row, column, char)

        self.cells_per_char[char].append(cell)
        if cell.is_solved():
            self.__save_solved_value(cell)
        self.move_count += 1
        if display:
            print(f"-- Move {self.move_count} ----")
            self.display(row, column, char)

    def __validate_char(self, char):
        if len(char) != 1 or char not in self.valid_chars:
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
            self.display(row, column, char, error=True)
            raise ValueError(
                f"Wrong value inserted [y='{row}', x='{column}', insert='{char}', expected='{solution_cell}']"
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

    def display(self, accent_row=None, accent_column=None, accent_char=None, error=False):
        def row_separator():
            print(GRID_SIZE * "----" + (GRID_SIZE + 1) * "-")

        color = colorama.Fore.GREEN if not error else colorama.Fore.RED

        def print_accent(s, y, x, char, end="\n"):
            if y == accent_row and x == accent_column:
                s = s.replace(char, color + char + colorama.Style.RESET_ALL)
            print(s, end=end)

        row_separator()
        for y in range(GRID_SIZE):
            print("|", end="")
            for x in range(GRID_SIZE):
                print_accent(f" {self.get_cell(y, x).to_str(False)} |", y, x, accent_char, end="")
            print()
            row_separator()

    def get_unsolved_associations(self, row, column):
        cell = self.get_cell(row, column)
        char = str(cell).strip()
        if len(char) != 1:
            return set()
        return self.solved_values.get_unsolved_associations(char)

    def get_unsolved_complementary_chars(self, char):
        return self.solved_values.get_unsolved_associations(char)

    def is_solved(self):
        return self.solved_count == GRID_SIZE ** 2

    class SolvedValues:
        # TODO: avoir des références à des cells
        def __init__(self, valid_letters, valid_digits):
            self.letters = {}
            for letter in valid_letters:
                self.letters[letter] = []
            self.digits = {}
            for digit in valid_digits:
                self.digits[digit] = []

        def __getitem__(self, char):
            if char.isalpha():
                return self.letters[char]
            return self.digits[char]

        def get_unsolved_associations(self, char):
            if char.isalpha():
                return set(self.letters[char]) ^ set(self.digits)
            return set(self.digits[char]) ^ set(self.letters)

        def __str__(self):
            res = "Solved values:\n"
            for letter in self.letters:
                res += "| "
                for digit in self.digits:
                    if digit in self.letters[letter]:
                        res += letter + digit
                    else:
                        res += "  "
                    res += " | "
                res += "\n"
            return res


if __name__ == "__main__":
    Grid.parse_value("")
