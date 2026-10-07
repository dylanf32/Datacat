import matplotlib.pyplot as mp
import seaborn as sns 
import numpy as np 


def scatterplot(df, x_column, y_column):

    fig, ax = plt.subplot()
    df.scatter(x_column, y_column, 
               )
    plt.show()

def boxplot(df,x_column):

    fig, ax = plt.subplots()
    VP = ax.boxplot(df[x_column], positions=[2, 4, 6], widths=1.5, patch_artist=True,
                showmeans=False, showfliers=False,
                medianprops={"color": "white", "linewidth": 0.5},
                boxprops={"facecolor": "C0", "edgecolor": "white",
                          "linewidth": 0.5},
                whiskerprops={"color": "C0", "linewidth": 1.5},
                capprops={"color": "C0", "linewidth": 1.5})

    ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
       ylim=(0, 8), yticks=np.arange(1, 8))

    plt.show()


def violin_plot(df,x_column):

    fig, ax = plt.subplots()

    vp = ax.violinplot(df[x_column],
                        [2, 4, 6],
                        widths=2,
                        showmeans=False,
                        showmedians=False,
                        showextrema=False)
    # styling:
    for body in vp['bodies']:
        body.set_alpha(0.9)
    ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
         ylim=(0, 8), yticks=np.arange(1, 8))

    plt.show()

def histogram_plot(df, x_column):

    sns.displot(data=df[x_column],x=x_column,kind="kde", multiple= "stack" )

def heatmap_plot(df):

    sns.heatmap(df, annot= True)








