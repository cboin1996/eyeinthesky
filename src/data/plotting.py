import matplotlib.pyplot as plt 

def bar(x,y):
    plt.bar(x, y)

def scatter(x,y, x_label, y_label, ax, annotate=False):
    ax.scatter(x, y)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if annotate:
        for i, txt in enumerate(y):
            if type(y) is float:
                txt = round(txt,1)
            ax.annotate(round(txt,2), (x[i], y[i]))

def pie(x):
    """
    Arguments:
        x (list-like) : the list of items to plot
    """
    plt.pie(x)

def pd_bar(df, xlabel, ylabel, ax, rot, fontsize, labelled_bars=True, colors=None):
    if colors is not None:
        ax = df.plot.bar(rot=rot, fontsize=fontsize, ax=ax, color=colors)

    else:
        ax = df.plot.bar(rot=rot, fontsize=fontsize, ax=ax)

    labels = [l.get_text() for l in ax.get_xticklabels()]
    ax.set_xticklabels(labels, ha='right')
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    

    for p in ax.patches:
        if labelled_bars:
            ax.annotate(str(round(p.get_height(), 2)), (p.get_x()+p.get_width()/2., p.get_height()),
                        ha='center', va='center', fontsize=7, fontweight='bold')
 

def pd_pie(df, ax, column, fontsize):
    ax = df.plot.pie(y=column, ax=ax, autopct=lambda p : '{:.2f}% ({:,.0f})'.format(p, p*df[column].sum()/100), fontsize=fontsize,
                     labeldistance=None, radius=1, startangle=160)
    ax.legend(labels=df.index, loc='best')
