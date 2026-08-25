import json

from app.core.logging import configure_logging, get_logger


def test_configure_logging_sets_up_structlog():
    configure_logging()
    logger = get_logger()
    assert logger is not None


def test_logger_outputs_valid_json(capsys):
    configure_logging()
    logger = get_logger()
    bound = logger.bind(tracking_id="abc-123", component="test")
    bound.info("test_event", value=42)
    output = capsys.readouterr().out
    parsed = json.loads(output)
    assert parsed["event"] == "test_event"
    assert parsed["value"] == 42
    assert parsed["tracking_id"] == "abc-123"
    assert parsed["component"] == "test"


def test_logger_includes_log_level(capsys):
    configure_logging()
    logger = get_logger()
    logger.info("level_check")
    output = capsys.readouterr().out
    parsed = json.loads(output)
    assert "level" in parsed


def test_configure_logging_is_idempotent(capsys):
    configure_logging()
    configure_logging()
    logger = get_logger()
    logger.info("idempotent_check")
    output = capsys.readouterr().out
    parsed = json.loads(output)
    assert parsed["event"] == "idempotent_check"
