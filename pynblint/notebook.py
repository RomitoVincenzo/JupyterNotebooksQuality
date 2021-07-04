import json
from pathlib import Path

import nbformat
from nbconvert import PythonExporter

from pynblint import nb_linting


class Notebook:
    """
    This class stores the representations of a notebook
    on which pynblint functions are called
    """

    def __init__(self, notebook_path: Path, repository_path: Path = None, notebook_name: str = None):
        self.path = notebook_path
        self.repository_path = repository_path
        self.notebook_name = notebook_name

        # Read the raw notebook file
        with open(self.path) as f:
            _nb_raw = f.read()

        # Convert the notebook to a Python dictionary
        self.nb_dict = json.loads(_nb_raw)

        # Convert the notebook to a Python script
        _nb_node = nbformat.reads(_nb_raw, as_version=self.nb_dict['nbformat'])
        python_exporter = PythonExporter()
        self.script, _ = python_exporter.from_notebook_node(_nb_node)

    def get_pynblint_results(self, bottom_size: int = 4,  filename_max_length=None):

        if self.notebook_name is not None:
            nb_name = self.notebook_name
        elif self.repository_path is not None:
            nb_name = str(self.path.relative_to(self.repository_path))
        else:
            nb_name = str(self.path)

        results = {
            "notebookName": nb_name,
            "notebookStats": {
                "numberOfCells": nb_linting.count_cells(self),
                "numberOfMDCells": nb_linting.count_md_cells(self),
                "numberOfCodeCells": nb_linting.count_code_cells(self),
                "numberOfRawCells": nb_linting.count_raw_cells(self),
            },
            "lintingResults": {
                "linearExecutionOrder": nb_linting.has_linear_execution_order(self),
                "numberOfClassDefinitions": nb_linting.count_class_defs(self),
                "numberOfFunctionDefinitions": nb_linting.count_func_defs(self),
                "allImportsInFirstCell": nb_linting.are_imports_in_first_cell(self),
                "numberOfMarkdownLines": nb_linting.count_md_lines(self),
                "numberOfMarkdownTitles": nb_linting.count_md_titles(self),
                "bottomMarkdownLinesRatio": nb_linting.get_bottom_md_lines_ratio(self, bottom_size),
                "nonExecutedCells": nb_linting.count_non_executed_cells(self),
                "emptyCells": nb_linting.count_empty_cells(self),
                "bottomNonExecutedCells": nb_linting.count_bottom_non_executed_cells(self, bottom_size),
                "bottomEmptyCells": nb_linting.count_bottom_empty_cells(self, bottom_size),
                "isTitled": nb_linting.is_titled(self),
                "isFilenameCharsetRestricted": nb_linting.is_filename_charset_restricted(self),
                "isNotCopied": nb_linting.is_not_copy(self)
            }
        }
        if filename_max_length is not None:
            results["lintingResults"]["isFilenameShort"] = nb_linting.is_filename_short(self, filename_max_length)
        return results

