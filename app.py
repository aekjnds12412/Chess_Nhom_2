"""Run with `python app.py` or `python app.py --server`."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor'))

if __name__=='__main__':
    if '--server' in sys.argv:
        sys.argv.remove('--server')
        from chessnet.server import main
        main()
    elif '--test' in sys.argv:
        import unittest
        suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(not result.wasSuccessful())
    else:
        from chessnet.gui import main
        main()
