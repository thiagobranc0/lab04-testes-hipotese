"""Um comando: python build.py  -> roda a simulação (se preciso) e gera images/ e README.md."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent/'src'))
root = pathlib.Path(__file__).parent
if '--resimular' in sys.argv or not (root/'data/processed/simulacao.csv').exists():
    import simulate; simulate.main()
import runpy; runpy.run_path(str(root/'src/readme.py'))
print('Pronto: README.md e images/ atualizados.')
