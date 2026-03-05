"""
Custom Exceptions
Application-specific exception classes
"""

from fastapi import HTTPException, status


class GeoNewsException(Exception):
    """Base exception for GeoNews application"""
    pass


class DatabaseException(GeoNewsException):
    """Database-related exceptions"""
    pass


class NLPException(GeoNewsException):
    """NLP processing exceptions"""
    pass


class GeocodingException(GeoNewsException):
    """Geocoding service exceptions"""
    pass


# HTTP Exceptions for API
class NotFoundException(HTTPException):
    """Resource not found"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ServiceUnavailableException(HTTPException):
    """Service temporarily unavailable"""
    def __init__(self, detail: str = "Service temporarily unavailable"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


class BadRequestException(HTTPException):
    """Bad request"""
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
