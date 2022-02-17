"""Linting functions for notebooks."""

import ast
import re
from typing import Dict, List, Optional

from nbformat.notebooknode import NotebookNode
from pydantic import BaseModel

from .notebook import Notebook


class NotebookLinterOptions(BaseModel):
    bottom_size: int = 4
    filename_max_length: Optional[int] = None


class NotebookLinter:
    def __init__(self, notebook: Notebook) -> None:
        self.options: NotebookLinterOptions = NotebookLinterOptions()

        self.results: Dict = {
            "notebookName": notebook.path.name,
            "notebookStats": {
                "numberOfCells": count_cells(notebook),
                "numberOfMDCells": count_md_cells(notebook),
                "numberOfCodeCells": count_code_cells(notebook),
                "numberOfRawCells": count_raw_cells(notebook),
            },
            "lintingResults": {
                "linearExecutionOrder": has_linear_execution_order(notebook),
                "numberOfClassDefinitions": count_class_defs(notebook),
                "numberOfFunctionDefinitions": count_func_defs(notebook),
                "allImportsInFirstCell": are_imports_in_first_cell(notebook),
                "numberOfMarkdownLines": count_md_lines(notebook),
                "numberOfMarkdownTitles": count_md_titles(notebook),
                "bottomMarkdownLinesRatio": get_bottom_md_lines_ratio(
                    notebook, self.options.bottom_size
                ),
                "nonExecutedCells": count_non_executed_cells(notebook),
                "emptyCells": count_empty_cells(notebook),
                "bottomNonExecutedCells": count_bottom_non_executed_cells(
                    notebook, self.options.bottom_size
                ),
                "bottomEmptyCells": count_bottom_empty_cells(
                    notebook, self.options.bottom_size
                ),
                "isTitled": is_titled(notebook),
                "isFilenameCharsetRestr": is_filename_charset_restricted(notebook),
            },
        }
        # if filename_max_length is not None:
        #     results["lintingResults"]["isFilenameShort"] =
        #                                                  is_filename_short(
        #         self, filename_max_length
        #     )

    def get_linting_results(self):
        return self.results


def count_func_defs(notebook: Notebook):
    """
    Count the number of function definitions in a notebook.

    Args:
        notebook(Notebook): python object representing the notebook
    Returns:
        f_num: integer representing the number of function definitions in the code

    A way you might use me is::

       function_defs_count = count_func_defs(nb)

    """
    code = notebook.script
    tree = ast.parse(code)
    f_num = sum(isinstance(exp, ast.FunctionDef) for exp in tree.body)
    return f_num


def count_non_executed_cells(notebook: Notebook):
    """
    Count the number of non-executed cells in a notebook.

    Args:
       notebook(Notebook): python object representing the notebook
    Returns:
        _non_executed_cells_count(notebook["cells"]): integer representing the number of
        non-executed cells in the notebook

    A way you might use me is

    non-exec_cells_count = count_non_executed_cells(nb)
    """
    nb_dict = notebook.nb_dict
    return _non_executed_cells_count(nb_dict["cells"])


def count_empty_cells(notebook: Notebook):
    """
    Count the number of empty cells in a notebook.

    Args:
       notebook(Notebook): python object representing the notebook
    Returns:
        _empty_cells_count(nb_dict["cells"]): integer representing the number of
        empty cells in the notebook

    A way you might use me is

    empty_cells_count = count_empty_cells(nb)
    """
    nb_dict = notebook.nb_dict
    return _empty_cells_count(nb_dict["cells"])


def count_md_lines(notebook: Notebook):
    """
    Count the number of markdown rows in a notebook.

    Args:
       notebook(Notebook): python object representing the notebook
    Returns:
        markdowns: integer representing the number of markdown rows in the notebook

    A way you might use me is

    md_lines_count = count_md_lines(nb)
    """
    nb_dict = notebook.nb_dict
    markdown_lines = 0
    for cell in nb_dict["cells"]:
        if cell["cell_type"] == "markdown":
            rows = len(cell["source"].split("\n"))
            markdown_lines += rows
    return markdown_lines


def count_md_titles(notebook: Notebook):
    """
    Count the number of markdown title rows in a notebook.

    Args:
       notebook(Notebook): python object representing the notebook
    Returns:
        titles: integer representing the number of markdown title rows in the notebook

    A way you might use me is

    titles_count = count_md_titles(nb)
    """
    nb_dict = notebook.nb_dict
    titles = 0
    for cell in nb_dict["cells"]:
        if cell["cell_type"] == "markdown":
            for row in cell["source"]:
                if row.lstrip().startswith("#"):
                    titles = titles + 1
    return titles


def are_imports_in_first_cell(notebook: Notebook):
    """
    Verifies if there are no import statements in cells that are not the first one.

    Args:
        notebook(Notebook): python object representing the notebook
    Returns:
        True if all the import are in the first cell of code, False otherwise

    A way you might use me is::

        all_imports_in_first_cell = are_imports_in_first_cell(nb)
    """

    code = notebook.script
    found_first_cell = False
    # when `found_first_cell` is True, it means we have found the first cell of code
    # that has to be ignored

    second_cell_not_reached = True
    # when set to False, we are actually reading instructions from the second cell of
    # code; from now on we need to analyze all the cells looking for import statements

    correct_position = True
    cell = ""
    program = code.split("\n")
    for line in program:
        if not found_first_cell:
            # it ignores all the lines before the first cell generated by
            # nbconvert(python# version ecc.)
            if line[0:5] == "# In[":
                found_first_cell = True
        elif not second_cell_not_reached:
            # starting from the second cell, it saves all the instructions until
            # it finds a new cell
            if line[0:5] != "# In[":
                cell = cell + "\n" + line
            else:
                tree = ast.parse(cell)
                # once it finds a new cell, it checks if there are any import statements
                # in the previous cell
                if sum(isinstance(exp, ast.Import) for exp in tree.body) > 0:
                    correct_position = False
                    break
        else:
            if line[0:5] == "# In[":
                # following instructions are from the second cell of code,
                # the first one we have to analyze
                second_cell_not_reached = False
    return correct_position


def has_linear_execution_order(notebook: Notebook):
    """
    Checks that notebook cells were executed in sequential order.

    The function takes a notebook and returns True if the cells are executed in
    sequential order,starting from 1, and False otherwise.

        Verifies if the notebook has been run in sequential order, starting from 1

        Args:
            notebook(Notebook): python object representing the notebook
        Returns:
            correct_exec: boolean value that is True if notebook cells have been
            sequentially run top to bottom

        A way you might use me is

        linear_exec_order = has_linear_execution_order(nb)
    """
    correct_exec = True
    counter = 1
    nb_dict = notebook.nb_dict
    for cell in nb_dict["cells"]:
        if cell["cell_type"] == "code":
            if counter == cell["execution_count"]:
                counter = counter + 1
            else:
                if cell["source"]:
                    correct_exec = False
    return correct_exec


def count_class_defs(notebook: Notebook):
    """
    Returns the number of class definitions found in the notebook cells.

        Args:
            notebook(Notebook): python object representing the notebook
        Returns:
            class_def_num: integer value representing the number of class definitions
            in the python code

        A way you might use me is

        class_def_count = count_class_defs(nb)
    """
    code = notebook.script
    tree = ast.parse(code)
    class_def_num = sum(isinstance(exp, ast.ClassDef) for exp in tree.body)
    return class_def_num


def _non_executed_cells_count(cell_list: List[NotebookNode]):
    """The function takes a list of cells and returns the number of non-executed cells.

    Args:
        cell_list(list): list of dictionary objects representing the notebook cells
    Returns:
        non_exec_cells: number of non-executed cells in the list

    The function is used in:
    - count_non-executed_cells(nb)
    - count_bottom_non-executed_cells(nb, bottom_size=4)
    """
    non_exec_cells = 0
    for cell in cell_list:
        if cell["cell_type"] == "code":
            if cell["execution_count"] is None and len(cell["source"]) > 0:
                non_exec_cells = (
                    non_exec_cells + 1
                )  # This is a not executed Python Cell containing actual code
    return non_exec_cells


def _empty_cells_count(cell_list: List[NotebookNode]):
    """The function takes a list of cells and returns the number of empty cells.

    Args:
        cell_list(list): list of dictionary objects representing the notebook cells
    Returns:
        empty_cells: number of empty cells in the list

    The function is used in:
    - count_empty_cells(nb)
    - count_bottom_empty_cells(nb, bottom_size=4)
    """
    empty_cells = 0
    for cell in cell_list:
        if cell["cell_type"] == "code":
            if cell["execution_count"] is None and len(cell["source"]) == 0:
                empty_cells += 1  # This is an empty Python Cell
    return empty_cells


def count_bottom_non_executed_cells(notebook: Notebook, bottom_size: int = 4):
    """
    Number of non-executed cells between the last bottom-size-cells of the notebook.

    Precondition: In order for the bottom of the notebook to actually represent
    the last section of it, it should not be more then the 33.3% of the whole notebook.
    In other words, the bottom_size should be minor then the dimension of the notebook
    divided by 3.

    Args:
        notebook(Notebook): python object representing the notebook
        bottom_size(int): number of cells starting from the bottom of the dictionary
    Returns:
        _non_executed_cells_count(cell_list): number of non-executed cells
        in the bottom-size last section of the notebook.
        None: in case the precondition is not satisfied

    A way you might use me is

    bottom_non_executed_cells = count_bottom_non_executed_cells(nb)
    """
    nb_dict = notebook.nb_dict
    if bottom_size < (
        len(nb_dict["cells"]) / 3
    ):  # puo essere sostituito con la funzione count_cells() una volta creata
        cell_list = _extract_bottom_cells_of_code(nb_dict, bottom_size)
    else:
        return None
    return _non_executed_cells_count(cell_list)


def count_bottom_empty_cells(notebook: Notebook, bottom_size: int = 4):
    """
    Number of empty cells between the last bottom-size-cells of the notebook.

    Precondition: In order for the bottom of the notebook to actually represent
    the last section of it, it should not be more then the 33.3% of the whole notebook.
    In other words, the bottom_size should be minor then the dimension of the notebook
    divided by 3.

    Args:
        notebook(Notebook): python object representing the notebook
        bottom_size(int): number of cells starting from the bottom of the dictionary
    Returns:
        _empty_cells_count(cell_list): number of empty cells in the bottom-size
        last section of the notebook.
        None: in case the precondition is not satisfied

    A way you might use me is

    bottom_empty_cells = count_bottom_empty_cells(nb)
    """
    nb_dict = notebook.nb_dict
    if bottom_size < (
        len(nb_dict["cells"]) / 3
    ):  # puo essere sostituito con la funzione count_cells() una volta creata
        cell_list = _extract_bottom_cells_of_code(nb_dict, bottom_size)
    else:
        return None
    return _empty_cells_count(cell_list)


def _extract_bottom_cells_of_code(nb_dict: NotebookNode, bottom_size: int):
    """
    It returns a list of code cells between the last bottom_size cells of the notebook.

    Args:
        nb_dict(dict): python dictionary object representing the jupyter notebook
        bottom_size(int): number of cells starting from the bottom of the dictionary
    Returns:
       cell_list: list of code cells between the last bottom_size cells of the notebook

    The function is used in:
    - count_bottom_empty_cells()
    - count_bottom_non_executed_cells()
    """
    cell_list = []
    counter = 1
    full_list = nb_dict["cells"]
    for cell in reversed(full_list):
        if counter <= bottom_size:
            if cell["cell_type"] == "code":
                cell_list.append(cell)
                counter = counter + 1
        else:
            break
    return cell_list


def count_cells(notebook: Notebook):
    """
    The function takes a notebook and returns the number of cells.

        Args:
            notebook(Notebook): python object representing the notebook
        Returns:
            len(nb_dict["cells"]): integer value representing the number of cells
            in the notebook

        A way you might use me is

        cells_count = count_cells(nb)
    """
    nb_dict = notebook.nb_dict
    return len(nb_dict["cells"])


def count_md_cells(notebook: Notebook):
    """
    The function takes a notebook and returns the number of markdown cells.

        Args:
            notebook(Notebook): python object representing the notebook
        Returns:
            counter: integer value representing the number of markdown cells
            in the notebook

        A way you might use me is

        md_cells_count = count_md_cells(nb)
    """
    nb_dict = notebook.nb_dict
    counter = 0
    for cell in nb_dict["cells"]:
        if cell["cell_type"] == "markdown":
            counter = counter + 1
    return counter


def count_code_cells(notebook: Notebook):
    """
    The function takes a notebook and returns the number of code cells.

        Args:
            notebook(Notebook): python object representing the notebook
        Returns:
            counter: integer value representing the number of code cells in the notebook

        A way you might use me is

        code_cell_count = count_code_cells(nb)
    """
    nb_dict = notebook.nb_dict
    counter = 0
    for cell in nb_dict["cells"]:
        if cell["cell_type"] == "code":
            counter = counter + 1
    return counter


def count_raw_cells(notebook: Notebook):
    """
    The function takes a notebook and returns the number of raw cells.

        Args:
            notebook(Notebook): python object representing the notebook
        Returns:
            counter: integer value representing the number of raw cells in the notebook

        A way you might use me is

        raw_cells_count = count_raw_cells(nb)
    """
    nb_dict = notebook.nb_dict
    counter = 0
    for cell in nb_dict["cells"]:
        if cell["cell_type"] == "raw":
            counter = counter + 1
    return counter


def get_bottom_md_lines_ratio(notebook: Notebook, bottom_size: int = 4):
    """
    Percentage of MD rows in the last cells of a notebook over the total MD rows.

    Precondition: In order for the bottom of the notebook to actually represent the last
    section of it, it should not be more then the 33.3% of the whole notebook.
    In other words, the bottom_size should be minor then the dimension of the notebook
    divided by 3.

    Args: notebook(Notebook): python object representing the notebook

    Returns: md_bottom_cells/md_first_cells: Percentage of markdown rows
    in the last cells of the notebook.
    None: in case the precondition is not satisfied

    A way you might use me is

    last_ten_cells_md_ratio = get_bottom_md_lines_ratio(nb, 10)
    """
    nb_dict = notebook.nb_dict
    total_cells = count_cells(notebook)
    if bottom_size < total_cells / 3:
        md_first_cells = 0
        md_bottom_cells = 0
        cell_counter = 1
        for cell in nb_dict["cells"]:
            if (
                cell_counter <= total_cells - bottom_size
                and cell["cell_type"] == "markdown"
            ):
                md_first_cells = md_first_cells + len(cell["source"].split("\n"))
            elif (
                cell_counter > total_cells - bottom_size
                and cell["cell_type"] == "markdown"
            ):
                md_bottom_cells = md_bottom_cells + len(cell["source"].split("\n"))
            cell_counter = cell_counter + 1
    else:
        return None
    if md_first_cells + md_bottom_cells == 0:
        return 0
    else:
        return md_bottom_cells / (md_first_cells + md_bottom_cells)


def is_titled(notebook: Notebook):
    """
    Checks whether a notebook was titled or not.

    Returns `False` if a notebook has still the default title: "Untitled.ipynb"

        Args:
            notebook(Notebook): python object representing the notebook
        Returns:
            boolean: False if the name of the notebook is Untitled, True otherwise

        A way you might use me is

        untitled = is_titled(notebook)
    """
    if notebook.path.name == "Untitled.ipynb":
        return False
    else:
        return True


def is_filename_charset_restricted(notebook: Notebook):
    """
    The function takes a notebook and checks whether it has a title
    with characters comprised in the ``[A-Za-z0-9_.-]`` charset

        Args:
            notebook(Notebook): python object representing the notebook
        Returns:
            boolean: True if the name of the notebook is withing the charset,
            False otherwise

        A way you might use me is

        restricted_filename = is_filename_charset_restricted(notebook)
    """
    if re.search("^[A-Za-z0-9_.-]+$", notebook.path.name):
        return True
    else:
        return False


def is_filename_short(notebook: Notebook, filename_max_length: int):
    """
    The function takes a notebook and checks whether it has a short title.

        Args:
            filename_max_length: threshold length under which the notebook filename
            is considered "short"
            notebook(Notebook): python object representing the notebook
        Returns:
            boolean: True if the name of the notebook is > than filename_max_length,
            False otherwise

        A way you might use me is

        short_filename = is_filename_short(notebook)
    """
    if len(notebook.path.name) > filename_max_length:
        return False
    else:
        return True
