"""Library specific errors."""


class FreeTierCloudClientLimitError(RuntimeError):
    """Limited usage of the free tier cloud client exceeded."""


class ClientResolutionError(RuntimeError):
    """Failed resolution of an unspecified client."""
