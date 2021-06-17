import logging
import tkinter as tk
import os, sys
import datetime 

from src.widgets import button,label, frame, entry
import src.http.api
import src.data.reporting
import src.otto.processing
from src import config
logger = logging.getLogger(__name__)

class Home:
    def __init__(self, title, base_path):
        logger.info("Hello World")
        self.title = title
        self.base_path = base_path
        self.data_path = os.path.join(self.base_path, config.data_dir)

    def open(self, root_window):
        title_frame = frame.Frame(root_window=root_window, height=25, bg="Gray", side="top")
        title_frame.pack()
        title_label = label.Label(title_frame, self.title)
        title_label.pack()

        """ Date for query"""
        start_date_entry_frame = frame.Frame(root_window=root_window, height=5, bg="white", side="left")
        start_date_entry_frame.pack()
        start_date_entry_default = tk.StringVar()
        fleet_today_date = datetime.datetime.now()-datetime.timedelta(2)
        start_date_entry_default.set(fleet_today_date.strftime("%Y-%m-%d"))
        start_date_entry = entry.Entry(root=start_date_entry_frame, width=10, bg="gray", fg="white", textvariable=start_date_entry_default)
        start_date_entry.pack()

        """Offset Date to use when looking at data"""
        offset_date_entry_frame = frame.Frame(root_window=root_window, height=5, bg="white", side="left")
        offset_date_entry_frame.pack()
        offset_date_entry_default = tk.StringVar()
        fleet_offset_date = datetime.datetime(year=datetime.datetime.now().year, month=datetime.datetime.now().month, 
                                              day=1, hour=19, minute=40, second=0)
        offset_date_entry_default.set(fleet_offset_date.strftime(config.offset_date_time_fmt))
        offset_date_entry = entry.Entry(root=offset_date_entry_frame, width=20, bg="gray", fg="white", textvariable=offset_date_entry_default)
        offset_date_entry.pack()

        """Button for getting the missions"""
        missions_button_frame = frame.Frame(root_window=root_window, height=10, bg="Gray", side="right")
        missions_button_frame.pack()
        missions_button = button.Button(missions_button_frame, display_text="GET Missions", 
                                        width=20, height=10, bg="Gray", fg="White", command=lambda: src.http.api.get_missions(self.data_path, self.title, start_date=start_date_entry.get()))
        missions_button.pack()

        plot_button_frame = frame.Frame(root_window=root_window, height=10, bg="Blue", side="left")
        plot_button_frame.pack()
        plot_button = button.Button(plot_button_frame, display_text="Graphs and report!", 
                                    width=20,height=10, bg="Gray", fg="White", command=lambda: src.otto.processing.missions_analysis(os.path.join(self.data_path, "missions.csv"),
                                                                                                                                    config.freqs, config.output_sep, config.global_ftempl,
                                                                                                                                    config.processed_res_dir, offset_date=offset_date_entry.get(),
                                                                                                                                    offset_positive=True))
        plot_button.pack()

        report_button_frame = frame.Frame(root_window=root_window, height=10, bg="Blue", side="left")
        report_button_frame.pack()
        report_button = button.Button(report_button_frame, display_text="Generate a report!", 
                                    width=20,height=10, bg="Gray", fg="White", command=lambda: src.data.reporting.create_latex(config.processed_res_dir, 
                                        open_when_done=True, author=config.report_author, title=config.report_title, company=config.report_company,
                                        logo_fpath=config.report_logo_fpath))
        report_button.pack()