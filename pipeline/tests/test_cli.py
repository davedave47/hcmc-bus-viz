import pytest

from busanalytics_pipeline.cli import COMMANDS, main


def test_commands_are_build_and_validate() -> None:
    assert COMMANDS == ("build", "validate")


def test_main_build_returns_zero(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["build"])
    assert code == 0
    assert "build" in capsys.readouterr().out
