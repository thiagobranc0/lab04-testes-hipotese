"""Um comando: python build.py -> roda a simulação (se preciso) e gera images/ e README.md.

Use `python build.py --resimular` para refazer a simulação mesmo que data/processed/ já exista.
"""
import pathlib
import runpy
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src import simulate  # noqa: E402

if '--resimular' in sys.argv or not (ROOT / 'data/processed/simulacao.csv').exists():
    simulate.main()
runpy.run_path(str(ROOT / 'src/readme.py'))
print('Pronto: README.md e images/ atualizados.')
