import sys
import _ast
from pyflakes import checker, __version__
from pyflakes import reporter as modReporter
from pyflakes import messages

PYFLAKES_ERROR_MESSAGES = [
    messages.DoctestSyntaxError,
    messages.ContinueOutsideLoop,
    messages.BreakOutsideLoop,
    messages.UndefinedName,
    # messages.UndefinedLocal,
    # messages.ForwardAnnotationSyntaxError,
    messages.StringDotFormatExtraPositionalArguments,
    messages.FStringMissingPlaceholders,
    messages.UnusedImport,
    messages.ImportShadowedByLoopVar,
    messages.DuplicateArgument,
    messages.TwoStarredExpressions,
    messages.DefaultExceptNotLast,
    messages.TooManyExpressionsInStarredAssignment,
    messages.ImportStarNotPermitted,
    messages.ImportStarUsed
]


def check(codeString, filename, reporter=None):
    """
    Check the Python source given by C{codeString} for flakes.
    @param codeString: The Python source to check.
    @type codeString: C{str}
    @param filename: The name of the file the source came from, used to report
        errors.
    @type filename: C{str}
    @param reporter: A L{Reporter} instance, where errors and warnings will be
        reported.
    @return: The number of warnings emitted.
    @rtype: C{int}
    """
    if reporter is None:
        reporter = modReporter._makeDefaultReporter()
    # First, compile into an AST and handle syntax errors.
    tree = compile(codeString, filename, "exec", _ast.PyCF_ONLY_AST)
    # Okay, it's syntactically valid.  Now check it.
    w = checker.Checker(tree, filename)
    w.messages.sort(key=lambda m: m.lineno)
    count = 0
    for message in w.messages:
        if message.__class__ in PYFLAKES_ERROR_MESSAGES:
            count += 1
            print("Error:")
            reporter.flake(message)
    if count > 0:
        raise Exception(f"Error occurred, please fix it first, Total errors: {count}")
