"""Smoke checks for the initial command-line scaffold."""

from aura.cli import main


def test_status_command(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["aura", "status"])
    assert main() == 0
    assert "solvers are not implemented yet" in capsys.readouterr().out
