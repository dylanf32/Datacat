import matplotlib.pyplot as plt
import seaborn as sns


def scatterplot(df, x_column, y_column, *, show=True):

    fig, ax = plt.subplots()

    ax.scatter(df[x_column], df[y_column])
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)

    if show:
        plt.show()

    return fig


def boxplot(df, x_column, *, show=True):

    fig, ax = plt.subplots()

    ax.boxplot(
        df[x_column].dropna(),
        positions=[1],
        widths=0.5,
        patch_artist=True,
        showmeans=False,
        showfliers=True,
        medianprops={"color": "white", "linewidth": 0.5},
        boxprops={"facecolor": "C0", "edgecolor": "white",
                  "linewidth": 0.5},
        whiskerprops={"color": "C0", "linewidth": 1.5},
        capprops={"color": "C0", "linewidth": 1.5}
    )

    ax.set_xticks([1])
    ax.set_xticklabels([x_column])
    ax.set_ylabel(x_column)

    if show:
        plt.show()

    return fig


def violin_plot(df, x_column, *, show=True):

    values = df[x_column].dropna()

    if values.nunique() < 2:
        raise ValueError("A violin plot needs at least two distinct values.")

    fig, ax = plt.subplots()

    vp = ax.violinplot(
        values,
        positions=[1],
        widths=0.8,
        showmeans=False,
        showmedians=False,
        showextrema=False
    )

    for body in vp["bodies"]:
        body.set_alpha(0.9)

    ax.set_xticks([1])
    ax.set_xticklabels([x_column])
    ax.set_ylabel(x_column)

    if show:
        plt.show()

    return fig


def histogram_plot(df, x_column, *, show=True):

    fig, ax = plt.subplots()

    sns.histplot(data=df, x=x_column, ax=ax)

    if show:
        plt.show()

    return fig


def heatmap_plot(df, *, show=True):

    correlation = df.corr(numeric_only=True)

    if correlation.empty:
        raise ValueError("A correlation heatmap needs numeric columns.")

    fig, ax = plt.subplots()

    sns.heatmap(
        correlation,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        ax=ax
    )

    plt.tight_layout()
    if show:
        plt.show()

    return fig


def bar_chart(df, x_column, y_column):

    fig, ax = plt.subplots()

    sns.barplot(data=df, x=x_column, y=y_column, ax=ax)
    

    return fig

def box_plot(df,x_column):

    fig, ax = plt.subplots()

    ax.boxplot(df[x_column].dropna())
    
    return fig
