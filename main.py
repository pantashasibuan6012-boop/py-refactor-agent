#!/usr/bin/env python3
"""PyRefactor Agent - Automated Python code modernization."""

import ast, sys, json
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Issue:
    line: int
    kind: str
    detail: str


@dataclass
class FileReport:
    path: str
    issues: list = field(default_factory=list)
    debt_score: float = 0.0


class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []

    def visit_FunctionDef(self, node):
        if not node.returns:
            self.issues.append(Issue(node.lineno, "missing_return", f"def {node.name}"))
        for arg in node.args.args:
            if arg.arg != "self" and not arg.annotation:
                self.issues.append(Issue(node.lineno, "missing_hint", arg.arg))
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ExceptHandler(self, node):
        if node.type is None:
            self.issues.append(Issue(node.lineno, "bare_except", "catch all"))
        self.generic_visit(node)


class RefactorEngine:
    WEIGHTS = {"missing_return": 2.5, "missing_hint": 1.5, "bare_except": 5.0, "mutable_default": 3.0}

    def __init__(self, target: str):
        self.target = Path(target)
        self.reports = []

    def scan(self):
        for py in sorted(self.target.rglob("*.py")):
            try:
                tree = ast.parse(py.read_text(), filename=str(py))
                a = Analyzer()
                a.visit(tree)
                if a.issues:
                    debt = sum(self.WEIGHTS.get(i.kind, 2.0) for i in a.issues)
                    self.reports.append(FileReport(str(py), a.issues, debt))
            except SyntaxError:
                pass
        return self.reports

    def summary(self):
        return {
            "files": len(list(self.target.rglob("*.py"))),
            "issues": sum(len(r.issues) for r in self.reports),
            "debt": round(sum(r.debt_score for r in self.reports), 1),
            "files_affected": len(self.reports),
        }


def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py [scan|report] <dir>")
        sys.exit(1)

    cmd, target = sys.argv[1], sys.argv[2]
    engine = RefactorEngine(target)

    if cmd == "scan":
        engine.scan()
        print(json.dumps(engine.summary(), indent=2))
        for r in engine.reports:
            for i in r.issues:
                print(f"  {r.path}:{i.line} [{i.kind}] {i.detail}")
    else:
        print(f"Unknown: {cmd}")


if __name__ == "__main__":
    main()
