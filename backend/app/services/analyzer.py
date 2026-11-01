"""Lightweight AST-based checks that need no external tools."""

import ast


def make_issue(severity, title, line, suggestion, kind):
    return {
        "severity": severity,
        "title": title,
        "line": max(1, line),
        "suggestion": suggestion,
        "source": "ast",
        # Stable identifier used to drop duplicates reported by other analyzers.
        "kind": kind,
    }


def _exported_names(tree: ast.AST) -> set[str]:
    """Names listed in ``__all__`` count as used (re-exports)."""
    names = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
            continue
        if isinstance(node.value, (ast.List, ast.Tuple)):
            for element in node.value.elts:
                if isinstance(element, ast.Constant) and isinstance(element.value, str):
                    names.add(element.value)
    return names


def analyze_python(code: str) -> list[dict]:
    issues = []

    try:
        tree = ast.parse(code)
    except SyntaxError as error:
        return [
            make_issue(
                "high",
                f"Syntax error: {error.msg}",
                error.lineno or 1,
                "Correct the syntax at this line before running the code.",
                "syntax-error",
            )
        ]
    except (ValueError, RecursionError) as error:
        return [
            make_issue(
                "high",
                f"Syntax error: {error}",
                1,
                "The code could not be parsed. Check for invalid characters or extreme nesting.",
                "syntax-error",
            )
        ]

    imported_names = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                imported_names[name] = node.lineno

        elif isinstance(node, ast.ImportFrom):
            # `from __future__ import ...` is a compiler directive, never "unused".
            if node.module == "__future__":
                continue
            for alias in node.names:
                if alias.name != "*":
                    name = alias.asname or alias.name
                    imported_names[name] = node.lineno

    used_names = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    used_names |= _exported_names(tree)

    for name, line in imported_names.items():
        if name not in used_names and not name.startswith("_"):
            issues.append(
                make_issue(
                    "low",
                    f"Unused import: {name}",
                    line,
                    f"Remove the import of '{name}' if it is not needed.",
                    "unused-import",
                )
            )

    function_types = (ast.FunctionDef, ast.AsyncFunctionDef)

    for node in ast.walk(tree):
        if isinstance(node, function_types):
            # Positional defaults apply to the *last* positional parameters,
            # including positional-only ones.
            positional = node.args.posonlyargs + node.args.args
            defaults = list(
                zip(
                    positional[len(positional) - len(node.args.defaults):],
                    node.args.defaults,
                )
            )
            defaults.extend(
                (arg, default)
                for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults)
                if default is not None
            )

            for argument, default in defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    issues.append(
                        make_issue(
                            "medium",
                            f"Mutable default argument: {argument.arg}",
                            default.lineno,
                            "Use None as the default and create a new "
                            "mutable object inside the function.",
                            "mutable-default",
                        )
                    )

        elif isinstance(node, ast.ExceptHandler):
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                issues.append(
                    make_issue(
                        "medium",
                        "Empty exception handler",
                        node.lineno,
                        "Handle the exception, log it, or re-raise it "
                        "instead of silently ignoring it.",
                        "empty-except",
                    )
                )

    return sorted(issues, key=lambda issue: issue["line"])
