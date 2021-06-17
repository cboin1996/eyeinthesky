
import os, sys

base_path = sys.path[0]

settings_fname = "settings.json"

data_dir = os.path.join(base_path, ".data")
processed_res_dir = os.path.join(data_dir, "results")
reporting_dir = os.path.join(data_dir, "reports")
reporting_dir = os.path.join(data_dir, "reports")

global_ftempl = "%s summary"
year_ftempl = "year%s"
month_ftempl = "month%s"
day_ftempl = "day%s"

offset_date_time_fmt = "%Y-%m-%d %H:%M:%S"

freqs = ["M", "D"]

required_dirs = [data_dir, processed_res_dir, reporting_dir]

log_dir = ".out"

settings_path = os.path.join(data_dir, settings_fname)

output_sep = "--------------------%s------------------"

report_author = "Christian Boin"
report_company = "JMP Solutions"
report_title = "KCPX Mission Analysis"
report_logo_fpath = os.path.join(base_path, "src", "assets", "jmp.png")


