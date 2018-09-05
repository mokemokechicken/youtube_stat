import re
from logging import getLogger

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf

from youtube_stat.config import Config
from youtube_stat.data.processor import DataProcessor
from youtube_stat.lib.datetime_util import parse_date_str
from youtube_stat.lib.file_util import load_json_from_file

logger = getLogger(__name__)


class Analyser:
    def __init__(self, config: Config):
        self.config = config

    def start(self):
        dp = DataProcessor(self.config)
        df = dp.load_training_data()

        words = load_json_from_file(dp.word_index_path)
        for w, i in list(words.items()):
            words[f"w{i:03d}"] = w

        self.plot_distribution(df)
        self.plot_group_distribution(dp)
        self.analyze("log_view", df, np.log(df.view), words)
        self.analyze("like_rate", df, df.like / df.view, words)

    def plot_distribution(self, df):
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 6))

        sns.distplot(df.view, kde=False, ax=axes[0, 0])
        axes[0, 0].set_title("View Count Distribution")

        sns.distplot(df.like, kde=False, ax=axes[0, 1])
        axes[0, 1].set_title("Like Count Distribution")

        sns.distplot(df.dislike, kde=False, ax=axes[1, 0])
        axes[1, 0].set_title("Dislike Count Distribution")

        sns.distplot(df.comment, kde=False, ax=axes[1, 1])
        axes[1, 1].set_title("Comment Count Distribution")

        plt.subplots_adjust(hspace=0.4)

        fig.savefig(f"{self.config.resource.working_dir}/{self.config.resource.summary_dist_graph_name}")

        ###
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 3))

        sns.distplot(np.log(df.view), kde=False, ax=axes[0])
        axes[0].set_title("Log(View Count) Distribution")

        sns.distplot(df.like / df.view, kde=False, ax=axes[1])
        axes[1].set_title("Like/View Rate Distribution")
        fig.savefig(f"{self.config.resource.working_dir}/{self.config.resource.target_dist_graph_name}")

    def plot_group_distribution(self, dp: DataProcessor):
        bdf = dp.load_basic_data()
        bdf['month'] = bdf.apply(lambda r: parse_date_str(r.date).strftime("%Y-%m"), axis=1)

        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 5))
        sns.boxplot(bdf.month, bdf.view, order=sorted(bdf.month.unique()), ax=ax)
        ax.set_title("view by month")
        fig.savefig(f"{self.config.resource.working_dir}/view_by_month.png")

        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 5))
        sns.boxplot(bdf.wday, bdf.view, order=sorted(bdf.wday.unique()), ax=ax)
        ax.set_title("view by weekday(0=Mon ~ 6=Sun")
        fig.savefig(f"{self.config.resource.working_dir}/view_by_weekday.png")

        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 5))
        sns.boxplot(bdf.month, bdf.like / bdf.view, order=sorted(bdf.month.unique()), ax=ax)
        ax.set_title("like rate by month")
        fig.savefig(f"{self.config.resource.working_dir}/like_rate_by_month.png")

    def analyze(self, name, df, df_y, words):
        template = open(self.config.resource.resource_dir / self.config.resource.summary_template_name, "rt").read()
        params = {"name": name}

        x_cols = [x for x in df.columns if re.search(r"^(201|Mon|Tue|Wed|Thr|Fri|Sat|Sun|w)", x)]

        df_x = df.loc[:, x_cols]
        df_x = sm.add_constant(df_x, prepend=False)
        model = smf.OLS(df_y, df_x, hasconst=True)
        result = model.fit()
        summary = result.summary2()
        params["stat1"] = summary.tables[0].to_html(header=False, index=False)
        params["stat2"] = summary.tables[2].to_html(header=False, index=False)

        coef_df = summary.tables[1]
        cf = coef_df[coef_df['P>|t|'] < 0.1].loc[:, "Coef."]

        wdf = {}
        ddf = {}
        for k, v in dict(cf).items():
            if k in words:
                wdf[words[k]] = v
            else:
                ddf[k] = v
        import_vars = pd.DataFrame(list(sorted([[k, v] for k, v in wdf.items()], key=lambda x: x[1])))
        import_vars.columns = ["word", "Coef"]
        coef_df.index = [words.get(x, x) for x in coef_df.index]

        params['coef_table'] = coef_df.round(3).to_html()
        params['important_table'] = import_vars.round(3).to_html(header=True, index=False)

        with open(f"{self.config.resource.working_dir}/{name}_summary.html", "wt") as f:
            f.write(template % params)
