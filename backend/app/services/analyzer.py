
import ast


def make_issue(severity, title, line, suggestion):
    return {
        "severity": severity,
        "title": title,
        "line": max(1, line),
        "suggestion": suggestion,
    }


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
            )
        ]

    imported_names = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                imported_names[name] = node.lineno

        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    name = alias.asname or alias.name
                    imported_names[name] = node.lineno

    used_names = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and isinstance(node.ctx, ast.Load)
    }

    for name, line in imported_names.items():
        if name not in used_names and not name.startswith("_"):
            issues.append(
                make_issue(
                    "low",
                    f"Unused import: {name}",
                    line,
                    f"Remove the import of '{name}' if it is not needed.",
                )
            )

    function_types = (ast.FunctionDef, ast.AsyncFunctionDef)

    for node in ast.walk(tree):
        if isinstance(node, function_types):
            positional_defaults = zip(
                node.args.args[-len(node.args.defaults):]
                if node.args.defaults
                else [],
                node.args.defaults,
            )

            defaults = list(positional_defaults)
            defaults.extend(
                (arg, default)
                for arg, default in zip(
                    node.args.kwonlyargs,
                    node.args.kw_defaults,
                )
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
                        )
                    )

        elif isinstance(node, ast.ExceptHandler):
            if (
                len(node.body) == 1
                and isinstance(node.body[0], ast.Pass)
            ):
                issues.append(
                    make_issue(
                        "medium",
                        "Empty exception handler",
                        node.lineno,
                        "Handle the exception, log it, or re-raise it "
                        "instead of silently ignoring it.",
                    )
                )

    return sorted(issues, key=lambda issue: issue["line"])
