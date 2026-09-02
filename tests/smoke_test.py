import ast
from pathlib import Path

root=Path(__file__).parents[1]
for p in root.rglob('*.py'):
    if p.name != 'smoke_test.py':
        ast.parse(p.read_text(encoding='utf-8'))
print('PASS: Python syntax check')
