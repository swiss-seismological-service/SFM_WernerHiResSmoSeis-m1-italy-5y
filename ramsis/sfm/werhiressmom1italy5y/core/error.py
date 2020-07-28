"""
Error and exception facilities.
"""
import enum
from ramsis.utils.error import Error, ErrorWithTraceback

# Examples of Error codes

class ModelExitCode(enum.Enum):
    EXIT_SUCCESS = 0
    EXIT_WARNING = 1
    EXIT_ERROR = 2


class WerHiResSmoM1Italy5yCoreError(ErrorWithTraceback):
    """Base WerHiResSmoM1Italy5y model core error ({})."""

class WerHiResSmoM1Italy5yObspyCatalogError(ErrorWithTraceback):
    """Input quakeml to obspy error ({})."""

class WerHiResSmoM1Italy5yWellInputError(ErrorWithTraceback):
    """Input well and finding hydraulic samples error ({})."""

class SeismicEventThresholdError(Error):
    """Too few seismic events found, model will not continue."""

class ExpectedModelConfigError(ErrorWithTraceback):
    """Expected a default parameter to be set in config: {}."""

class NegativeVolumeError(ErrorWithTraceback):
    """Negative cumulative volume in training period."""
