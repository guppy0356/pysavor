import pkgutil
import inspect
import importlib

__path__ = pkgutil.extend_path(__path__, __name__)

for importer, modname, ispkg in pkgutil.iter_modules(path=__path__, prefix=__name__ + "."):
    module = importlib.import_module(modname)

    for name, obj in inspect.getmembers(module):
        if (
            inspect.isclass(obj)
            and hasattr(obj, "__table__")
            and obj.__module__ == module.__name__
        ):
            globals()[name] = obj
