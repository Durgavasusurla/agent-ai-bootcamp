import pytest

from agent.tools import NoteStore, calculator


def test_calculator_basic():
    assert calculator("(12 + 7) * 3") == "57"
    assert calculator("2 ** 10") == "1024"
    assert calculator("10 / 4") == "2.5"


def test_calculator_rejects_code():
    with pytest.raises(Exception):
        calculator("__import__('os').system('echo hi')")


def test_notes_round_trip(tmp_path):
    store = NoteStore(tmp_path / "notes.json")
    assert store.list() == "no notes saved yet"
    assert store.save("buy milk") == "saved note #1"
    assert "1. buy milk" in store.list()
