class MissingMethodException(Exception):
    """Exception raised when a required method is not implemented."""

class CyclicDependencyException(Exception):
    """Exception raised when cyclic dependencies are detected."""