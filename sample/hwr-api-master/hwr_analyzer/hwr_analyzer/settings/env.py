import sys
from pathlib import Path
import environ

TESTING = len(sys.argv) >= 2 and sys.argv[1] == 'test'

# django-environ
# http://django-environ.readthedocs.org
_ROOT = environ.Path(__file__) - 4  # kasa-api/

if not TESTING and Path(_ROOT('.env')).exists():
    environ.Env.read_env(env_file=_ROOT('.env'))

ENV = environ.Env(
    # set casting, default value
    DEBUG=(bool, True),
)
