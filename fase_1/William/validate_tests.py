"""Script de validação dos testes sem executá-los."""

import ast
import sys
from pathlib import Path

def validate_test_file(filepath):
    """Valida um arquivo de teste sem executar."""
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        
        # Parse AST
        tree = ast.parse(code)
        
        # Verificar classes de teste
        test_classes = []
        test_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.startswith('Test'):
                    test_classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    test_functions.append(node.name)
        
        return {
            'filepath': str(filepath),
            'valid': True,
            'test_classes': test_classes,
            'test_functions': test_functions,
            'error': None
        }
    except SyntaxError as e:
        return {
            'filepath': str(filepath),
            'valid': False,
            'error': str(e)
        }

# Validar todos os testes
test_files = list(Path('tests').glob('test_*.py'))
print(f"Validando {len(test_files)} arquivos de teste...\n")

all_valid = True
total_tests = 0

for test_file in sorted(test_files):
    result = validate_test_file(test_file)
    
    if result['valid']:
        n_classes = len(result['test_classes'])
        n_functions = len(result['test_functions'])
        total = n_classes + n_functions
        total_tests += total
        
        print(f"✅ {test_file.name}")
        print(f"   Classes: {n_classes}, Functions: {n_functions}, Total: {total}")
        if result['test_classes']:
            print(f"   Classes: {', '.join(result['test_classes'][:3])}")
    else:
        print(f"❌ {test_file.name}")
        print(f"   Erro: {result['error']}")
        all_valid = False

print(f"\n{'='*60}")
print(f"Total de testes encontrados: {total_tests}")
print(f"Arquivo principais validados: {'✅ SIM' if all_valid else '❌ NÃO'}")
print(f"{'='*60}")

sys.exit(0 if all_valid else 1)
