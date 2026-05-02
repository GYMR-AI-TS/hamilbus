### test_helpers.py
### AI generated

from hamilbus.helpers import save_array, load_array, save_dict, load_dict, save_list, load_list

import json
from pathlib import Path

import numpy as np
import pytest


# Fixture
@pytest.fixture()
def tmp(tmp_path, monkeypatch):
    """Change cwd to a fresh temp directory for every test."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


# save_array
def test_save_array_returns_absolute_path(tmp):
    result = save_array(np.array([1, 2, 3]), "data")
    assert result.is_absolute()


def test_save_array_extension_added_automatically(tmp):
    result = save_array(np.zeros(5), "no_ext")
    assert result.suffix == ".npy"
    assert result.exists()


def test_save_array_extension_replaced_if_wrong(tmp):
    result = save_array(np.zeros(5), "data.txt")
    assert result.suffix == ".npy"
    assert result.exists()


def test_save_array_npy_extension_preserved(tmp):
    result = save_array(np.zeros(5), "data.npy")
    assert result.suffix == ".npy"


def test_save_array_file_created_on_disk(tmp):
    path = save_array(np.arange(10), "myarray")
    assert path.exists()


def test_save_array_relative_path_lands_in_cwd(tmp):
    path = save_array(np.ones(3), "relative")
    assert path.parent == tmp.resolve()


def test_save_array_absolute_path_respected(tmp):
    abs_path = tmp / "subdir" / "arr"
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    result = save_array(np.ones(3), abs_path)
    assert result.parent == (tmp / "subdir").resolve()


def test_save_array_1d_roundtrip(tmp):
    arr = np.array([10, 20, 30])
    path = save_array(arr, "arr1d")
    assert np.array_equal(np.load(path), arr)


def test_save_array_2d_float_roundtrip(tmp):
    arr = np.random.rand(4, 4)
    path = save_array(arr, "arr2d")
    assert np.allclose(np.load(path), arr)


def test_save_array_empty_array(tmp):
    arr = np.array([])
    path = save_array(arr, "empty")
    assert np.array_equal(np.load(path), arr)


def test_save_array_path_object_accepted(tmp):
    result = save_array(np.zeros(2), Path("pathobj"))
    assert result.exists()


# load_array
def test_load_array_basic_roundtrip(tmp):
    arr = np.array([1.0, 2.0, 3.0])
    path = save_array(arr, "rt")
    assert np.array_equal(load_array(path), arr)


def test_load_array_relative_path_resolves_from_cwd(tmp):
    arr = np.arange(5)
    save_array(arr, "rel")
    assert np.array_equal(load_array("rel.npy"), arr)


def test_load_array_file_not_found_raises(tmp):
    with pytest.raises(FileNotFoundError):
        load_array(tmp / "ghost.npy")


def test_load_array_wrong_extension_raises_value_error(tmp):
    bad = tmp / "data.csv"
    bad.write_text("1,2,3")
    with pytest.raises(ValueError, match="Unsupported extension"):
        load_array(bad)


def test_load_array_no_extension_raises_value_error(tmp):
    no_ext = tmp / "data"
    no_ext.write_bytes(b"")
    with pytest.raises(ValueError, match="Unsupported extension"):
        load_array(no_ext)


def test_load_array_2d_array_preserved(tmp):
    arr = np.eye(3)
    path = save_array(arr, "eye")
    assert np.array_equal(load_array(path), arr)


def test_load_array_dtype_preserved(tmp):
    arr = np.array([1, 2], dtype=np.int16)
    path = save_array(arr, "dtype")
    assert load_array(path).dtype == np.int16


def test_load_array_string_path_accepted(tmp):
    arr = np.zeros(4)
    save_array(arr, "s")
    assert np.array_equal(load_array(str(tmp / "s.npy")), arr)


# save_dict
def test_save_dict_returns_absolute_path(tmp):
    result = save_dict({1.0: "one"}, "mydict")
    assert result.is_absolute()


def test_save_dict_json_extension_added(tmp):
    result = save_dict({}, "no_ext")
    assert result.suffix == ".json"
    assert result.exists()


def test_save_dict_extension_replaced(tmp):
    result = save_dict({}, "file.txt")
    assert result.suffix == ".json"


def test_save_dict_file_is_valid_json(tmp):
    path = save_dict({1.5: "a", 2.0: "b"}, "d")
    assert isinstance(json.loads(path.read_text()), dict)


def test_save_dict_keys_serialized_as_strings(tmp):
    path = save_dict({3.14: "pi"}, "pi")
    assert "3.14" in json.loads(path.read_text())


def test_save_dict_empty_dict(tmp):
    path = save_dict({}, "empty")
    assert json.loads(path.read_text()) == {}


def test_save_dict_path_object_accepted(tmp):
    path = save_dict({1.0: "x"}, Path("obj"))
    assert path.exists()


def test_save_dict_always_saves_in_cwd(tmp):
    path = save_dict({}, "wherever")
    assert path.parent == tmp.resolve()


# load_dict
def test_load_dict_basic_roundtrip(tmp):
    d = {1.0: "one", 2.5: "two point five"}
    save_dict(d, "rd")
    assert load_dict("rd") == d


def test_load_dict_keys_are_floats(tmp):
    save_dict({42.0: "answer"}, "kf")
    assert all(isinstance(k, float) for k in load_dict("kf"))


def test_load_dict_relative_path_resolves_from_cwd(tmp):
    save_dict({0.0: "zero"}, "rel")
    assert load_dict("rel") == {0.0: "zero"}


def test_load_dict_extension_added_if_missing(tmp):
    save_dict({1.0: "a"}, "ext_test")
    assert load_dict("ext_test") == {1.0: "a"}


def test_load_dict_file_not_found_raises(tmp):
    with pytest.raises(FileNotFoundError):
        load_dict(tmp / "missing.json")


def test_load_dict_absolute_path_accepted(tmp):
    path = save_dict({9.9: "nine"}, "abs_d")
    assert load_dict(path) == {9.9: "nine"}


def test_load_dict_empty_dict_roundtrip(tmp):
    save_dict({}, "empty")
    assert load_dict("empty") == {}


def test_load_dict_multiple_entries(tmp):
    d = {float(i): str(i) for i in range(10)}
    save_dict(d, "multi")
    assert load_dict("multi") == d


# save_list
def test_save_list_returns_absolute_path(tmp):
    result = save_list([1, 2, 3], "lst")
    assert result.is_absolute()


def test_save_list_json_extension_added(tmp):
    result = save_list([], "no_ext")
    assert result.suffix == ".json"
    assert result.exists()


def test_save_list_extension_replaced(tmp):
    result = save_list([], "file.txt")
    assert result.suffix == ".json"


def test_save_list_file_is_valid_json(tmp):
    path = save_list([1, "two", 3.0], "lst")
    assert isinstance(json.loads(path.read_text()), list)


def test_save_list_empty_list(tmp):
    path = save_list([], "empty")
    assert json.loads(path.read_text()) == []


def test_save_list_always_saves_in_cwd(tmp):
    path = save_list([0], "loc")
    assert path.parent == tmp.resolve()


def test_save_list_nested_list(tmp):
    nested = [[1, 2], [3, 4]]
    path = save_list(nested, "nested")
    assert json.loads(path.read_text()) == nested


def test_save_list_path_object_accepted(tmp):
    path = save_list([1], Path("obj"))
    assert path.exists()


# load_list
def test_load_list_basic_roundtrip(tmp):
    lst = [1, "hello", 3.14, True, None]
    save_list(lst, "rl")
    assert load_list("rl") == lst


def test_load_list_relative_path_resolves_from_cwd(tmp):
    save_list([7, 8], "rel")
    assert load_list("rel") == [7, 8]


def test_load_list_extension_added_if_missing(tmp):
    save_list([99], "ext_test")
    assert load_list("ext_test") == [99]


def test_load_list_file_not_found_raises(tmp):
    with pytest.raises(FileNotFoundError):
        load_list(tmp / "ghost.json")


def test_load_list_absolute_path_accepted(tmp):
    path = save_list(["a", "b"], "abs_l")
    assert load_list(path) == ["a", "b"]


def test_load_list_empty_list_roundtrip(tmp):
    save_list([], "empty")
    assert load_list("empty") == []


def test_load_list_nested_list_roundtrip(tmp):
    nested = [[1, 2], {"key": "val"}, [True, None]]
    save_list(nested, "nested")
    assert load_list("nested") == nested


def test_load_list_large_list(tmp):
    lst = list(range(10_000))
    save_list(lst, "large")
    assert load_list("large") == lst


def test_load_list_string_path_accepted(tmp):
    save_list([42], "strpath")
    assert load_list(str(tmp / "strpath.json")) == [42]


# Path edge cases
def test_save_array_overwrites_existing_file(tmp):
    path = save_array(np.array([1, 2, 3]), "over")
    save_array(np.array([9, 9, 9]), "over")
    assert np.array_equal(np.load(path), np.array([9, 9, 9]))


def test_save_dict_overwrites_existing_file(tmp):
    save_dict({1.0: "old"}, "over")
    save_dict({2.0: "new"}, "over")
    assert load_dict("over") == {2.0: "new"}


def test_save_list_overwrites_existing_file(tmp):
    save_list([1, 2], "over")
    save_list([9, 9], "over")
    assert load_list("over") == [9, 9]


def test_dict_and_list_same_stem_last_write_wins(tmp):
    # Both produce .json — the last save wins when stems collide.
    save_dict({1.0: "dict"}, "shared")
    save_list(["list"], "shared")
    assert load_list("shared") == ["list"]


def test_load_array_from_subdirectory(tmp):
    sub = tmp / "sub"
    sub.mkdir()
    arr = np.array([5, 6, 7])
    path = save_array(arr, sub / "arr")
    assert np.array_equal(load_array(path), arr)


def test_path_with_spaces(tmp):
    arr = np.zeros(3)
    path = save_array(arr, tmp / "my array")
    assert path.exists()
    assert np.array_equal(load_array(path), arr)


def test_deeply_nested_absolute_path_array(tmp):
    deep = tmp / "a" / "b" / "c"
    deep.mkdir(parents=True)
    arr = np.ones(2)
    path = save_array(arr, deep / "deep")
    assert np.array_equal(load_array(path), arr)


def test_load_dict_stem_only_name_finds_json(tmp):
    save_dict({3.0: "three"}, "stem_only")
    assert load_dict("stem_only") == {3.0: "three"}


def test_load_list_stem_only_name_finds_json(tmp):
    save_list(["x", "y"], "stem_only2")
    assert load_list("stem_only2") == ["x", "y"]
