from pynblint.notebook import Notebook
from pynblint.repository import LocalRepository
from pynblint import nb_linting, repo_linting
from pathlib import Path
import pytest

if __name__ == '__main__':
    pytest.main()


@pytest.fixture(scope="module")
def notebooks():
    nb1 = Notebook(Path("../fixtures", "FullNotebook2.ipynb"))
    nb2 = Notebook(Path("../fixtures", "FullNotebookFullNotebookFullNotebook.ipynb"))
    nb3 = Notebook(Path("../fixtures", "acs,.-e+.ipynb"))
    nb4 = Notebook(Path("../fixtures", "Untitled.ipynb"))
    nb5 = Notebook(Path("../fixtures", "FullNotebook2-Copy1.ipynb"))
    return {
        "FullNotebook2.ipynb": nb1,
        "FullNotebookFullNotebookFullNotebook.ipynb": nb2,
        "acs,.-e+.ipynb": nb3,
        "Untitled.ipynb": nb4,
        "FullNotebook2-Copy1.ipynb": nb5
    }


@pytest.fixture(scope="module")
def repos():
    folder1 = LocalRepository(Path("../fixtures", "test_repo", "UntitledNoDuplicates"))
    folder2 = LocalRepository(Path("../fixtures", "test_repo", "DuplicatesNoUntitled"))
    return {
        "UntitledNoDuplicates": folder1,
        "DuplicatesNoUntitled": folder2
    }


@pytest.mark.parametrize("test_input,expected", [
    ("FullNotebook2.ipynb", 3),
    ("FullNotebookFullNotebookFullNotebook.ipynb", 15)
])
def test_count_cells(test_input, expected, notebooks):
    assert nb_linting.count_cells(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("FullNotebook2.ipynb", 0),
    ("FullNotebookFullNotebookFullNotebook.ipynb", 5)
])
def test_count_md_cells(test_input, expected, notebooks):
    assert nb_linting.count_md_cells(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("acs,.-e+.ipynb", 0),
    ("FullNotebookFullNotebookFullNotebook.ipynb", 9)
])
def test_count_code_cells(test_input, expected, notebooks):
    assert nb_linting.count_code_cells(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("FullNotebook2.ipynb", 0),
    ("FullNotebookFullNotebookFullNotebook.ipynb", 1)
])
def test_count_raw_cells(test_input, expected, notebooks):
    assert nb_linting.count_raw_cells(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("FullNotebook2.ipynb", False),
    ("FullNotebookFullNotebookFullNotebook.ipynb", True)
])
def test_has_linear_execution_order(test_input, expected, notebooks):
    assert nb_linting.has_linear_execution_order(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("FullNotebook2.ipynb", 1),
    ("FullNotebookFullNotebookFullNotebook.ipynb", 0)
])
def test_count_class_defs(test_input, expected, notebooks):
    assert nb_linting.count_class_defs(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("FullNotebook2.ipynb", 0),
    ("FullNotebookFullNotebookFullNotebook.ipynb", 1)
])
def test_count_func_defs(test_input, expected, notebooks):
    assert nb_linting.count_func_defs(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("FullNotebook2.ipynb", False),
    ("FullNotebookFullNotebookFullNotebook.ipynb", True)
])
def test_are_imports_in_first_cell(test_input, expected, notebooks):
    assert nb_linting.are_imports_in_first_cell(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("FullNotebook2.ipynb", 0),
    ("FullNotebookFullNotebookFullNotebook.ipynb", 8)
])
def test_count_md_lines(test_input, expected, notebooks):
    assert nb_linting.count_md_lines(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("FullNotebook2.ipynb", 0),
    ("FullNotebookFullNotebookFullNotebook.ipynb", 1)
])
def test_count_md_titles(test_input, expected, notebooks):
    assert nb_linting.count_md_titles(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("FullNotebook2.ipynb", None),
    ("FullNotebookFullNotebookFullNotebook.ipynb", 0.375)
])
def test_get_bottom_md_lines_ratio(test_input, expected, notebooks):
    assert nb_linting.get_bottom_md_lines_ratio(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("FullNotebook2.ipynb", 0),
    ("Untitled.ipynb", 2)
])
def test_count_non_executed_cells(test_input, expected, notebooks):
    assert nb_linting.count_non_executed_cells(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("FullNotebook2.ipynb", 0),
    ("Untitled.ipynb", 1)
])
def test_count_empty_cells(test_input, expected, notebooks):
    assert nb_linting.count_empty_cells(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("FullNotebook2.ipynb", None),
    ("Untitled.ipynb", 1)
])
def test_count_bottom_non_executed_cells(test_input, expected, notebooks):
    assert nb_linting.count_bottom_non_executed_cells(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("FullNotebook2.ipynb", None),
    ("Untitled.ipynb", 1)
])
def test_count_bottom_empty_cells(test_input, expected, notebooks):
    assert nb_linting.count_bottom_empty_cells(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("FullNotebook2.ipynb", True),
    ("Untitled.ipynb", False)
])
def test_is_titled(test_input, expected, notebooks):
    assert nb_linting.is_titled(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("acs,.-e+.ipynb", False),
    ("Untitled.ipynb", True)
])
def test_is_filename_charset_restricted(test_input, expected, notebooks):
    assert nb_linting.is_filename_charset_restricted(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("FullNotebookFullNotebookFullNotebook.ipynb", False),
    ("Untitled.ipynb", True)
])
def test_is_filename_short(test_input, expected, notebooks):
    max_title_length = 20
    assert nb_linting.is_filename_short(notebooks[test_input], max_title_length) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("UntitledNoDuplicates", []),
    ("DuplicatesNoUntitled", [Path("../fixtures", "test_repo", "DuplicatesNoUntitled", "Test.ipynb"),
                              Path("../fixtures", "test_repo", "DuplicatesNoUntitled", "prova", "Test.ipynb")])
])
def test_get_duplicate_notebooks(test_input, expected, repos):
    assert repo_linting.get_duplicate_notebooks(repos[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("DuplicatesNoUntitled", []),
    ("UntitledNoDuplicates", [Path("../fixtures", "test_repo", "UntitledNoDuplicates", "Untitled.ipynb")])
])
def test_get_untitled_notebooks(test_input, expected, repos):
    assert repo_linting.get_untitled_notebooks(repos[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("FullNotebook2.ipynb", True),
    ("FullNotebook2-Copy1.ipynb", False)
])
def test_is_not_copy(test_input, expected, notebooks):
    assert nb_linting.is_not_copy(notebooks[test_input]) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("DuplicatesNoUntitled", [Path("../fixtures", "test_repo", "DuplicatesNoUntitled", "Test-Copy1.ipynb")]),
    ("UntitledNoDuplicates", [])
])
def test_get_copied_notebooks(test_input, expected, repos):
    assert repo_linting.get_copied_notebooks(repos[test_input]) == expected
