import os
import logging
import numpy as np
import pandas as pd
# from matplotlib import colormaps
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from backtest.base import Runner


log = logging.getLogger(__name__)



class BoxPlot:

    def __init__(self, runner: Runner):
        self.runner = runner

    def read_results(self, fn: str):
        """Read backtest results from CSV file"""
        df = pd.read_csv(fn)
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.dropna(inplace=True)
        # At least there are two closed trades
        return df[df['Total Closed Trades'] > 0 ]
    
    def boxplot(self, key = 'Total Return [%]'):
        """plot boxplot for given parameters

        params = [(3, 6, '1d'), (4, 8, '1d'), (5, 10, '1d')]
        
        """
        # Create figures from the output report
        boxes = list()
        labels = list()

        #
        # colors = list(mcolors.TABLEAU_COLORS.keys())
        colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)
        colors.pop('white')
        # by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgba(color)[:3])), name)
        #         for name, color in colors.items())
        # sorted_names = [name for _, name in by_hsv]
        sorted_names = list(colors.keys())
        # breakpoint()
        fig, ax = plt.subplots(figsize=(20, 10))
        i = 1

        # params is used to find CSV feeds
        for param in self.runner.iter_parameters():
            # for f, s, interval in params:
            # fn = os.path.join(out_dir, f'backtest_sma_{interval}_{f}x{s}.csv')
            # print(param)
            fp = self.runner.get_output_file(**param)
            if not os.path.exists(fp):
                continue

            # log.info("process %s", fn)
            log.info("process %s ...", fp)
            df = self.read_results(fp)
            # color = random.choice(colors)
            color = colors[sorted_names[i]]
            flierprops = dict(marker='o', markerfacecolor=color, markersize=5,
                    linestyle='none', markeredgecolor='b')
            
            # A box and whisker plot or diagram (otherwise known as a boxplot), 
            # is a graph summarising a set of data. The shape of the boxplot shows 
            # how the data is distributed and it also shows any outliers. It is a 
            # useful way to compare different sets of data as you can draw more 
            # than one boxplot per graph. These can be displayed alongside a number line, 
            # horizontally or vertically.
            # https://www.ncl.ac.uk/webtemplate/ask-assets/external/\
            # maths-resources/statistics/data-presentation/\
            # box-and-whisker-plots.html#:~:text=A%20box%20and%20whisker%20plot,than%20one%20boxplot%20per%20graph.
            box = ax.boxplot(df[key], 
                            positions=[i*2],
                            widths=1.5, 
                            patch_artist=True,
                            showmeans=True, 
                            showfliers=True, 
                            flierprops=flierprops,
                            medianprops={"color": "white", "linewidth": 0.5},
                            boxprops={"facecolor": color, "edgecolor": "white", "linewidth": 0.5},
                            whiskerprops={"color": color, "linewidth": 1.5},
                            capprops={"color": color, "linewidth": 1.5})
            boxes.append(box)
            label = self.runner.create_label(**param)
            # labels.append(f'{f}x{s}-{interval}')
            labels.append(label)
            i += 1
        ax.legend([b['boxes'][0] for b in boxes], labels)
        ax.set_title(key)
        fig.savefig(os.path.join(self.runner.get_work_dir(), f'{key}.png'))

    def create_plots(self):
        for name in self.runner.get_plots():
            log.info("Create plot for metric: %s ...", name)
            self.boxplot(key=name)
