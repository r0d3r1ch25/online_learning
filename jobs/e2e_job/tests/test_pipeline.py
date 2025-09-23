#!/usr/bin/env python3
"""
Simple tests for E2E pipeline job.
Tests basic functionality without complex async mocking.
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import log

class TestPipelineSimple:
    """Simple unit tests for pipeline functions"""
    
    def test_log_function(self, capsys):
        """Test log function outputs correctly"""
        log("Test message")
        captured = capsys.readouterr()
        assert "Test message" in captured.out
        assert captured.out.endswith("Test message\n")
    
    def test_imports(self):
        """Test that all required modules can be imported"""
        import asyncio
        import aiohttp
        import json
        import datetime
        assert True  # If we get here, imports worked

if __name__ == "__main__":
    pytest.main([__file__])