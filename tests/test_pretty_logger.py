"""Test pretty print logging functionality."""
from app.frameworks import logger

def test_pretty_logger():
    # Test JSON output
    json_log = logger.setup_logger(pretty=False)
    json_log.info("This is JSON formatted", key="value")
    
    # Test pretty print output
    pretty_log = logger.setup_logger(pretty=True)
    pretty_log.info("This is pretty printed", key="value")