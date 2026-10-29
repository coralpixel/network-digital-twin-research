
import importlib


def test_dependencies_importable():
    for name in ["networkx", "matplotlib", "pandas", "streamlit"]:
        importlib.import_module(name)


def test_package_importable():
    import ndt
