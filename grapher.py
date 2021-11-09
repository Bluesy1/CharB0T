import json
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

def graph(name,trueVotes):
    votesDf = pd.DataFrame(trueVotes)
    votesDf['average']= votesDf.mean(axis=1)
    votesDf = votesDf.reset_index()
    items = list(votesDf.columns)[1:]
    sns.set_theme(style="darkgrid")
    with PdfPages(name) as export_pdf:
        sns.displot(data=votesDf,kde=True,)
        export_pdf.savefig(dpi=250,bbox_inches='tight')
        plt.close()
        g = sns.scatterplot(data=votesDf)
        g.legend(loc='center left', bbox_to_anchor=(1.25, 0.5), ncol=1)
        export_pdf.savefig(dpi=250,bbox_inches='tight')
        plt.close()
        g = sns.lineplot(data=votesDf, palette="tab10", linewidth=2.5)
        g.legend(loc='center left', bbox_to_anchor=(1.25, 0.5), ncol=1)
        export_pdf.savefig(dpi=250,bbox_inches='tight')
        plt.close()
        for i in items:
            sns.displot(data=votesDf,x=i,kde=True,)
            export_pdf.savefig(dpi=250,bbox_inches='tight')
            plt.close()
            sns.boxplot(data=votesDf, x=i)
            export_pdf.savefig(dpi=250,bbox_inches='tight')
            plt.close()