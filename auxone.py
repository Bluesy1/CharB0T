from __future__ import print_function
from hikari.undefined import UNDEFINED
import lightbulb
from lightbulb.commands import user
import pandas as pd
import numpy as np
import json
import time
import matplotlib.pyplot as plt
import six
from matplotlib.backends.backend_pdf import PdfPages
from collections.abc import Sequence
from cryptography.fernet import Fernet
import math
import seaborn as sns
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Shadow
with open('details.json') as f:
    data = json.load(f) 

URL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['googleSheetId'],
    data['workSheetName'])
InvestorsURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['InvestersID'],
    data['Investorssheetgid'])
SSaccessURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['SSaccessID'],
    data['SSaccessgid'])
UserListURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['UserListID'],
    data['UserListgid'])
RPOInfoURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['RPOinfoID'],
    data['RPOinfogid']) 
RPOKnowledgeURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['RPOKnowledgeID'],
    data['RPOKnowledgegid'])

with open('filekey.key','rb') as file:
    key = file.read()
fernet = Fernet(key)

def render_mpl_table(data, col_width=5, row_height=0.625, font_size=20,
                     header_color='#40466e', row_colors=['xkcd:sky blue', 'xkcd:blue grey'], edge_color='k',
                     bbox=[0, 0, 1.3, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    plt.savefig('table.png',dpi=250,bbox_inches='tight')
    return ax

def as_currency(amount):
    if amount >= 0:
        return '${:,.2f}'.format(amount)
    else:
        return '-${:,.2f}'.format(abs(amount))

def as_percent(amount):
    if amount >= 0:
        return '{:,.2f}%'.format(amount)
    else:
        return '-{:,.2f}%'.format(abs(amount))
