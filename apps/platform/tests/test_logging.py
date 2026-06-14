def test_get_logger_returns_logger():
    from odp_platform.common.logging_utils import get_logger
    logger = get_logger("test_logging", log_type="test")
    assert logger is not None
    assert logger.name == "odp_platform.test_logging"
