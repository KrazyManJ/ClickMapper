from os.path import join as pathjoin,dirname,pardir,abspath,relpath

ROOT = dirname(__file__)

SAVED_MACRO_PATH = pathjoin(ROOT, pardir, "saved_macros.json")
MACRO_SCHEMA = pathjoin(ROOT, "macro", "macro_schema.json")

def ui_design_file(name):
    return pathjoin(ROOT, "ui", name)