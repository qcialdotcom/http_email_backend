"""
http_email_backend
==================

Public package interface.

Exposes the main email backend for direct import.
"""

from ._email import HttpProxyEmailBackend

__all__ = ["HttpProxyEmailBackend"]
