"""
Pages package initialization.
"""
from .backtest_page import render as render_backtest_page
from .download_page import render as render_download_page
from .enrich_page import render as render_enrich_page
from .storage_config_page import render as render_storage_config_page

__all__ = [
    'render_backtest_page',
    'render_download_page',
    'render_enrich_page',
    'render_storage_config_page'
]
