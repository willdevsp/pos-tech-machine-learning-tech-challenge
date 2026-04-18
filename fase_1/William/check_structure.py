"""Verificação de estrutura do projeto."""

from pathlib import Path
import sys

def check_project_structure():
    """Verifica estrutura do projeto."""
    
    print("🔍 Verificando estrutura do projeto...\n")
    
    # Estrutura esperada
    expected_dirs = [
        'src',
        'src/models',
        'src/data',
        'src/evaluation',
        'src/api',
        'tests',
        'data',
        'data/processed',
        'logs',
        'notebooks',
    ]
    
    expected_files = [
        'src/__init__.py',
        'src/config.py',
        'src/logging_config.py',
        'src/models/__init__.py',
        'src/models/pipeline.py',
        'src/models/transformers.py',
        'src/models/inference.py',
        'src/models/baseline.py',
        'src/data/__init__.py',
        'src/data/loader.py',
        'src/data/preprocessing.py',
        'src/evaluation/__init__.py',
        'src/evaluation/metrics.py',
        'src/api/__init__.py',
        'src/api/main.py',
        'src/api/schemas.py',
        'tests/__init__.py',
        'tests/conftest.py',
        'tests/test_config.py',
        'tests/test_preprocessing.py',
        'tests/test_models.py',
        'pyproject.toml',
        'Makefile',
        'ruff.toml',
        'README.md',
    ]
    
    # Verificar diretórios
    print("📁 Diretórios:")
    missing_dirs = []
    for d in expected_dirs:
        if Path(d).exists():
            print(f"  ✅ {d}/")
        else:
            print(f"  ❌ {d}/ (FALTANDO)")
            missing_dirs.append(d)
    
    print(f"\n📄 Arquivos:")
    missing_files = []
    for f in expected_files:
        if Path(f).exists():
            file_size = Path(f).stat().st_size
            print(f"  ✅ {f} ({file_size:,} bytes)")
        else:
            print(f"  ❌ {f} (FALTANDO)")
            missing_files.append(f)
    
    # Resumo
    print(f"\n{'='*70}")
    print(f"Diretórios: {len(expected_dirs) - len(missing_dirs)}/{len(expected_dirs)} ✅")
    print(f"Arquivos: {len(expected_files) - len(missing_files)}/{len(expected_files)} ✅")
    
    if missing_dirs or missing_files:
        print(f"\n❌ FALTAM: {len(missing_dirs)} diretórios, {len(missing_files)} arquivos")
        return False
    else:
        print(f"\n✅ Estrutura COMPLETA!")
        return True

if __name__ == "__main__":
    success = check_project_structure()
    sys.exit(0 if success else 1)
