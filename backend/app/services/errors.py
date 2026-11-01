class AnalyzerUnavailable(Exception):
    """An analyzer could not run (not installed, timed out, bad output...).

    This is not a problem with the submitted code, so it is reported to the user
    as a warning and never counts against the score.
    """
