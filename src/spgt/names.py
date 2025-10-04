import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ASP_CODE_DIR = os.path.abspath(os.path.join(ROOT_DIR, "asp"))
ASP_PLANNER_PATH = os.path.abspath(os.path.join(ASP_CODE_DIR, "regression_variable_planner.lp"))
ASP_REGRESSOR_PATH  = os.path.abspath(os.path.join(ASP_CODE_DIR, "regressor_variable.lp"))
ASP_CLINGRAPH_PATH = os.path.abspath(os.path.join(ASP_CODE_DIR, "clingraph_generator.lp"))
ASP_PPLTL_PLANNER_PATH = os.path.abspath(os.path.join(ASP_CODE_DIR, "reg_var_ppltl_planner.lp"))