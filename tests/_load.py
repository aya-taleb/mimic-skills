"""Load a skill's script as a module without installing anything."""
import importlib.util
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load(skill, script):
    path = os.path.join(ROOT, "skills", skill, "scripts", script + ".py")
    spec = importlib.util.spec_from_file_location("%s_%s" % (skill.replace("-", "_"), script), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
