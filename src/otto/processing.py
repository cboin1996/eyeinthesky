import pandas as pd
import logging 
import matplotlib.pyplot as plt 
import datetime
import os, sys
import logging
import numpy as np

from src.io import files
from src import config, util
from src.data import plotting, reporting, stats

import src.otto.processing
from src.otto import datakeys 
logger = logging.getLogger(__name__)

def initialize(processed_res_dir):
    old_data_folders = util.browse_dir(processed_res_dir, level=1)
    logger.info(f"Cleaning system files {old_data_folders} in folder {processed_res_dir}")
    util.rm_dirs(old_data_folders)

def missions_analysis(fp, freqs, output_sep, global_ftempl, processed_res_dir, showfigs=False, offset_date=None, offset_positive=True):
    logger.info("Lauching Mission Analysis.")
    initialize(processed_res_dir)

    raw_df = files.read_csv(fp)
    df = preprocess(raw_df, offset_date, offset_positive)
    """Create the global summary dashboard"""
    for fig_idx, freq in enumerate(freqs):
        """
        Initialize Directories for Plots
        """
        freq_processed_res_dir = os.path.join(processed_res_dir, freq)
        util.generate_dirs([freq_processed_res_dir])
        """
        Start with a global snapshot including all missions avg run time, and success percentage
        """
        df_summary, df_summary_count, df_summary_mean, df_summary_mean_successful = get_results(df, freq, output_sep, 
                                                                                        global_ftempl, freq_processed_res_dir)
        
        """
        For each mission type, create a dashboard with scatter plot for all missions times, 
        outputting the average time for that mission.
        Also, create a plot of successful versus cancelled, showing the total number of missions.
        """
        missions = df[datakeys.MISSION_TEMPL].unique()
        df_dt_index = set(df_summary_count.reset_index().set_index(datakeys.CREATED).index) # get the unique dt values for the freq
        for mission in missions:
            for dt in df_dt_index:
                get_detailed_results(df, mission, dt, freq, output_sep, global_ftempl, freq_processed_res_dir)


    plt.tight_layout()
    
    if showfigs:
        plt.show()

    reporting.create_latex(processed_res_dir, open_when_done=True, author=config.report_author, title=config.report_title, company=config.report_company,
                                        logo_fpath=config.report_logo_fpath)


def get_results(df, freq="D", output_sep="-----", global_ftempl="%s", processed_res_dir="res"):
    df_summary = df.copy()
    df_summary, df_outliers = stats.remove_outliers_from_cols(df_summary, [datakeys.EXECUTION_TIME])

    df_summary_grouped = df_summary.groupby([pd.Grouper(freq=freq), datakeys.MISSION_STATUS, datakeys.MISSION_TEMPL])
    df_summary_count = df_summary_grouped.count().rename(columns={datakeys.EXECUTION_TIME : datakeys.MISSION_COUNT})
    df_summary_mean = df_summary_grouped.mean()

    df_summary_mean_successful = df_summary[df_summary[datakeys.MISSION_STATUS].str.contains(datakeys.SUCCEEDED)].drop(columns=[datakeys.MISSION_STATUS])
    df_summary_mean_successful = df_summary_mean_successful.groupby([pd.Grouper(freq=freq), datakeys.MISSION_TEMPL]).mean()

    logger.info(output_sep % (f"GLOBAL SUMMARY {util.get_freq_english(freq)}"))
    util.print_df(df_summary_count, title="Mission Count")
    util.print_df(df_summary_mean, title="Mission Average Times")
    util.print_df(df_outliers, title="Outliers")

    total_missions_success, total_missions_failed, total_ratio = get_totals(df_summary_count)

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(17,12))

    sup_str = "\n".join((
        f"All time summary of every missions' average execution time and success rate per {util.get_freq_english(freq).lower()}",
        f"Success percentage: {total_ratio}%",
        f"All time successful: {total_missions_success}",
        f"All time cancelled: {total_missions_failed}",
        f"All time average execution time {round(df_summary_mean_successful['execution_time'].mean(), 2)}"
    ))

    fig.suptitle(sup_str, fontsize=10)

    plotting.pd_bar(df_summary_mean_successful, xlabel="", ylabel="Average execution time (s)", ax=axes[0], rot=10, fontsize=6)
    
    df_summary_count_unpacked = df_summary.copy()
    df_summary_count_unpacked[datakeys.MISSION_SUCCEEDED] = df_summary_count_unpacked[df_summary_count_unpacked[datakeys.MISSION_STATUS].str.contains(datakeys.SUCCEEDED)][datakeys.EXECUTION_TIME]
    df_summary_count_unpacked[datakeys.MISSION_CANCELLED] = df_summary_count_unpacked[df_summary_count_unpacked[datakeys.MISSION_STATUS].str.contains(datakeys.CANCELLED)][datakeys.EXECUTION_TIME]
    df_summary_count_unpacked.drop(columns=[datakeys.MISSION_STATUS], inplace=True)
    df_summary_count_unpacked = df_summary_count_unpacked.groupby([pd.Grouper(freq=freq), datakeys.MISSION_TEMPL]).count()
    df_summary_count_unpacked = df_summary_count_unpacked.rename(columns={datakeys.EXECUTION_TIME : datakeys.MISSION_COUNT})

    util.print_df(df_summary_count_unpacked, title="Mission Count Unpacked")
    plotting.pd_bar(df_summary_count_unpacked, xlabel="", ylabel="Number of missions", 
                                                 ax=axes[1], rot=10, fontsize=6, colors=["tab:blue", "tab:green", "tab:red"])

    data_dir = os.path.join(processed_res_dir, "Summary")
    util.generate_dirs([data_dir])
    """ Write CSVs"""
    summary_fname = os.path.join(data_dir, global_ftempl % (util.get_freq_english(freq)) + " all" + ".csv")
    mean_fname = os.path.join(data_dir, global_ftempl % (util.get_freq_english(freq)) + " mean" + ".csv")
    count_fname = os.path.join(data_dir, global_ftempl % (util.get_freq_english(freq)) + " count" + ".csv")
    outlier_fname = os.path.join(data_dir, global_ftempl % (util.get_freq_english(freq)) + " outlier" + ".csv")

    files.write_csv(df_summary, summary_fname)
    files.write_csv(df_summary_mean_successful, mean_fname)
    files.write_csv(df_summary_count, count_fname)
    files.write_csv(df_outliers, outlier_fname)

    """Save Figures"""
    fig_path = os.path.join(data_dir, global_ftempl % (util.get_freq_english(freq)) + " dashboard.png")
    files.savefig(fig, fig_path)

    return df_summary, df_summary_count, df_summary_mean, df_summary_mean_successful

def get_detailed_results(df, mission, datetime_val, freq, output_sep="-----", global_ftempl="%s", processed_res_dir="res"):
    df, df_outliers = stats.remove_outliers_from_cols(df, [datakeys.EXECUTION_TIME])

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(17,12))

    strf_time = datetime_val.strftime(get_date_str_fmt(freq))

    df_valid_date = df.loc[strf_time] # first filter data specific to the date
    df_valid = df_valid_date[df_valid_date[datakeys.MISSION_TEMPL] == mission] # filter data specific to the mission

    df_mission_grouped = df_valid.groupby([pd.Grouper(freq=freq), datakeys.MISSION_STATUS, datakeys.MISSION_TEMPL])
    df_mission_count = df_mission_grouped.count().rename(columns={datakeys.EXECUTION_TIME : datakeys.MISSION_COUNT})
    df_mission_successful = df_valid[df_valid[datakeys.MISSION_STATUS].str.contains(datakeys.SUCCEEDED)]
    df_mission_mean = df_mission_successful[datakeys.EXECUTION_TIME].mean()
    
    total_missions_success, total_missions_failed, total_ratio = get_totals(df_mission_count)

    sup_str_missions = "\n".join((
        f"{util.get_freq_english(freq)} ending {datetime_val}'s summary for {mission}",
        f"Average run time: {round(df_mission_mean, 2)}",
        f"Success percentage: {total_ratio}%",
        f"Total Successful: {total_missions_success}",
        f"Total Cancelled: {total_missions_failed}"
    ))

    fig.suptitle(sup_str_missions, fontsize=10)

    plotting.pd_pie(df_mission_count.reset_index().set_index(datakeys.MISSION_STATUS), ax=axes[0], column=datakeys.MISSION_COUNT, fontsize=10)
    plotting.scatter(df_mission_successful.index, df_mission_successful[datakeys.EXECUTION_TIME], x_label="Time of submission (month-day hour)", y_label="time (s)", ax=axes[1])

    filesafe_missionname = files.get_filesafe_str(mission)
    filesafe_date = files.get_filesafe_str(strf_time)

    data_dir = os.path.join(processed_res_dir, filesafe_date)
    util.generate_dirs([data_dir])
    """ Write CSVs"""
    mission_times_fname = os.path.join(data_dir, f"{filesafe_date}-{filesafe_missionname}.csv")
    outliers_fname = os.path.join(data_dir, f"{filesafe_date}-{filesafe_missionname} Outliers.csv")

    files.write_csv(df_mission_successful, mission_times_fname)
    files.write_csv(df_outliers, outliers_fname)

    """Save Figures"""
    fig_path = os.path.join(data_dir, f"{filesafe_date}-{filesafe_missionname}.png")
    files.savefig(fig, fig_path)

def get_totals(df):
    total_df = df.reset_index().groupby(datakeys.MISSION_STATUS).sum()
    if datakeys.SUCCEEDED in total_df.index:
        total_success = total_df.loc[datakeys.SUCCEEDED, datakeys.MISSION_COUNT]
    else:
        total_success = 0
    if datakeys.CANCELLED in total_df.index:
        total_failed = total_df.loc[datakeys.CANCELLED, datakeys.MISSION_COUNT]
    else:
        total_failed = 0

    total_ratio = round(100 - (total_failed/total_success)*100, 2)
    return total_success, total_failed, total_ratio

def preprocess(df, offset_date=None, offset_positive=True):
    df[datakeys.CREATED] = pd.to_datetime(df[datakeys.CREATED], format="%Y-%m-%dT%H:%M:%S.%fZ")

    if offset_date is not None:
        offset_datetime = datetime.datetime.strptime(offset_date, config.offset_date_time_fmt)
        offset_timedelta = pd.Timedelta(days=offset_datetime.day,
                                        hours=offset_datetime.hour, minutes=offset_datetime.minute,
                                                         seconds=offset_datetime.second)
        if offset_positive:
            df[datakeys.CREATED] = df[datakeys.CREATED] + offset_timedelta
        else:
            df[datakeys.CREATED] = df[datakeys.CREATED] - offset_timedelta

    df[datakeys.EXECUTION_TIME] = pd.to_timedelta(df[datakeys.EXECUTION_TIME]) # convert to datetime
    df[datakeys.EXECUTION_TIME] = df[datakeys.EXECUTION_TIME].dt.total_seconds()
    df = df.rename(columns={df.columns[4] : datakeys.MISSION_TEMPL})
    df = df[[datakeys.CREATED, datakeys.EXECUTION_TIME, datakeys.MISSION_STATUS, datakeys.MISSION_TEMPL]]
    df = df.reset_index(drop=True).set_index('created')
    return df

def get_dates(df, freq):
    if freq == "Y":
        dates = df[datakeys.CREATED].dt.year.unique()
    if freq == "M":
        dates = df[datakeys.CREATED].dt.month.unique()
    if freq == "D":
        dates = df[datakeys.CREATED].dt.day.unique()
    
    return dates

def get_date_str_fmt(freq):
    if freq == "Y":
        key = "%Y"
    if freq == "M":
        key = "%Y-%m"
    if freq == "D":
        key = "%Y-%m-%d"
    
    return key

