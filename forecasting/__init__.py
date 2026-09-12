"""Forecasting package for renewable generation (solar/wind) and load demand."""

try:
    from forecasting.predict import forecast
    __all__ = ["forecast"]
except ImportError:
    pass
