# PyRefactor Agent

An AI-powered code refactoring agent that scans legacy Python codebases and modernizes them automatically.

## Features
- Async migration for synchronous functions
- Type hint injection (parameters + return types)
- Technical debt scoring and reporting
- Security vulnerability detection

## Installation
```
pip install -r requirements.txt
```

## Usage
```
python main.py scan ./myproject
python main.py refactor ./myproject --dry-run
```

## License
MIT