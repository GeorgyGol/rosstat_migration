import re

def read_sum_migration(strSource):
    '''make DataFrame with GENERAL RESULTS OF MIGRATION from 1990, simply in and out, by all countries'''
    migr=pd.read_excel(strSource, sheetname=0, names=['MigrationIn', 'MigrationOut'],
                     parse_cols=[0,5,10], header=None, skiprows =8, skip_footer=54, index_col=0)
    migr.index.name='years'
    return migr

#print (read_sum_migration(strSumMigration))

def make_translate_dict(strSource):
    '''Make translation DICT, for rus-eng translation '''
    fl=open(strSource, 'r', encoding='utf-8')
    dctTranslate={}

    for ln in fl:
        ss=re.split('\t',ln)
        if len(ss) > 2:
            dctTranslate.setdefault(ss[0].strip(), ss[1].strip())
            dctTranslate.setdefault(ss[2].strip(), ss[3].strip())
    
    dct_ext={'Соединенные Штаты':'USA', 'Боливия, многонациональное государство':'Bolivia', 
         'Великобритания (Соединенное Королевство)':'United Kingdom', 'Иран, Исламская Республика':'Iran',
        'КНДР (Северная Корея)':'Korea, D.P.R.', 'Корея, Республика':'Korea', 'Южная Осетия':'South Ossetia',
        'Южная Африка':'South Africa', 'ЛИЦА БЕЗ ГРАЖДАНСТВА':'v.c.', "Кот-д’Ивуар":"Cote d'Ivoire", 
        'Конго':'Republic of the Congo', 'Конго, Демократическая Республика':'Democratic Republic of the Congo', 
        'Республика Македония':'Macedonia', 'Венесуэла, Боливарианская Республика':'Venezuela', 
        'Лаосская Народно-Демократическая Республика':'Lao P.D.R.', 'Тайвань (Китай)':'Taiwan', 
        'Молдова, Республика':'Moldova Republic', 'Палестина, Государство':'Palestine'}
    dctTranslate.update(dct_ext)
    return dctTranslate

#print(make_translate_dict(r'/home/egor/git/jupyter/Migration/coutries.txt'))

lst_CIS=[ 'Азербайджан', 'Армения', 'Беларусь', 'Казахстан', 'Киргизия', 
         'Республика Молдова', 'Таджикистан', 'Туркмения', 'Узбекистан', 'Украина', 'Молдова, Республика']

lst_exUSSR= lst_CIS + ['Латвия', "Литва", "Эстония", "Грузия"]

lst_exUSSR_nr = lst_exUSSR + ['Южная Осетия', 'Абхазия']

def make_dict(source_list, key='CIS', src_lst=lst_CIS):
    dct={ k.strip(): key if k.strip() in src_lst else 'FOREIGN' for k in source_list }
    return dct

def read_sum_migration_country(strSource, lstSplitRegion=lst_exUSSR):
    '''nake DataFrame with general results of migration by countries, from 1997'''
    migr=pd.read_excel(strSource, sheetname=0, header=0, skiprows =4, index_col=0).dropna()
        
    migr.index.rename('Country', inplace=True)

    dEx=make_dict(migr.index.tolist(), key='exUSSR', src_lst=lstSplitRegion)
    migr.reset_index(inplace=True)
    
    #print(dEx)
    
    migr['AREA2']=migr['Country'].map(dEx)
    migr['CountryEng']=migr['Country'].map(make_translate_dict('coutries.txt'))
    migr['DIRECTION']='in'
    
    migr['CountryEng']=migr['CountryEng'].str.strip()
    
    migr.set_index('Country', inplace=True)
    migr.loc['Южная Осетия', 'CountryEng']='South Ossetia'
    migr.loc['другие страны', 'CountryEng']='other countries'
    
    l=migr.index.get_loc('Выбыло из Российской Федерации - всего')
    migr.loc['Выбыло из Российской Федерации - всего':, 'DIRECTION']='out'
    migr.reset_index(inplace=True)
    
    m_del=migr[migr['CountryEng'].isnull()]
    
    m_del=m_del.where(m_del['Country'].str.contains('в|из\s'))
    migr.drop(m_del['Country'].dropna().index, inplace=True)
    
    migr.set_index('CountryEng', inplace=True)

    return migr

def make_plot_dataframe(dtfMain, strDirection, strArea, fScale):
    '''cleaning data from unrecognized states'''
    def cleaning_unrecognized_states(dtf, list_col):
        k2=dtf.loc[('Georgia', 'Abkhazia', 'South Ossetia'), list_col].sum()
        dtf.loc['Georgia', list_col]=k2
        drp=dtf.drop(['Abkhazia', 'South Ossetia'], inplace=True)
        return dtf
    
    mTemp=mgr[mgr['DIRECTION']==strDirection]
    mTemp=cleaning_unrecognized_states(mTemp, lstWorkCol)
    mRet=mTemp[mTemp['AREA2']==strArea]
    return mRet[lstWorkCol].div(fScale)


def set_spines(ax, *varg):
    '''turn out axes spines'''
    for pl in varg[0]:
        ax.spines[pl].set_visible(False)
        
def plot2bars(dfOut, dfIn, axOut, axIn, bar_colors_in=None, ano_lines=None, ano_lines_x=3.5, 
              bar_colors_out=None, stacked_bars=False, ax_legend=None, legend_labels=None, 
              strXLabel=strXlabel100, strYLabel=strXlabel100):
    '''plot two hor-bar sets, one against other'''
    def drw_ano_lines(axO, axI, dctLines, x_off):
        for key, val in dctLines.items():
            axO.axhline(color=strColorOut, linestyle='-', linewidth=fKeyLineWidth, y=key-iBaseYear)
            axI.axhline(color=strColorIn, linestyle='-', linewidth=fKeyLineWidth, y=key-iBaseYear)
            axI.annotate(val, xy=(axI.get_xlim()[0], key-iBaseYear), 
                     xytext=(axI.get_xlim()[0]+x_off, key-iBaseYear+0.2), ha='center', fontsize=8)

    
    dfOut.plot(kind='barh', ax=axOut, fontsize=iTickLabelSize, 
                           alpha=fAplha, color=bar_colors_out, width=fBarWidth, 
                           stacked=stacked_bars, legend=False)
    axOut.set_title(strOutTitle, fontsize=iAxisTitleSize, color=strColorOut)
    axOut.set_xlabel(strXLabel, fontsize=iTickLabelSize, color=strColorOut)
    axOut.get_yaxis().set_tick_params(labelsize=iTickLabelSize, colors=strColorOut)

    set_spines(axOut, ['top', 'right'])

    dfIn.plot(kind='barh', ax=axIn, fontsize=iTickLabelSize, 
                          alpha=fAplha, color=bar_colors_in, width=fBarWidth, stacked=stacked_bars, 
              legend=ax_legend != None)
    axIn.set_title(strInTitle, fontsize=iAxisTitleSize, color=strColorIn)

    axIn.invert_xaxis()
    set_spines(axIn, ['top'])
    axIn.spines['top'].set_visible(False)
    axIn.spines['left'].set_position('zero')
    axIn.get_yaxis().set_tick_params(direction='out', labelsize=iTickLabelSize, colors=strColorIn)
    axIn.get_yaxis().set_ticks_position('right')
    axIn.set_xlabel(strXLabel, fontsize=iTickLabelSize, color=strColorIn)
    axIn.get_yaxis().set_label_position('right')
    
    axOut.set_xlim([axIn.get_xlim()[1], axIn.get_xlim()[0]])
    
    if ano_lines:
        drw_ano_lines(axOut, axIn, ano_lines, ano_lines_x)
    
    
    axIn.set_xlim([axIn.get_xlim()[0]+2, axIn.get_xlim()[1]])

    axOut.set_xlim([axIn.get_xlim()[1], axIn.get_xlim()[0]])
    if ax_legend:
        move_legend(axIn, ax_legend, legend_labels)
        
def move_legend(axFrom, axTo, lstLabels=None):
    '''move legend to external axes'''
    axTo.axis('off')
    hdl, lbl = axFrom.get_legend_handles_labels()
    axTo.legend(hdl, lbl if not lstLabels else lstLabels, loc='center')
    axFrom.legend_.remove()

def print_text(ax, df, y_pos=0, step=12):
    '''print text for DataFrame with CULT colomn '''
    lstAnno=['Group members:']
    lst_cat=list(df['CULT'].unique().dropna())

    for i in range(len(lst_cat)):
        i_step=step
        lst_c=sorted(df[df['CULT']==lst_cat[i]].index.unique().dropna().tolist())
        lst_c[::i_step]=list(map(lambda x:x+'\n', lst_c[::i_step]))
        lst_c[0]=lst_c[0].strip()
        lstAnno.append('"{}": {}\n'.format(lst_cat[i], ', '.join(lst_c).replace('\n, ', ',\n')))
    ax.text(0, y_pos, '\n'.join(lstAnno), color='black', fontsize=8)     
    
def sum_and_sort(pdFrame, lstCols):
    pdFrame['sum']=pdFrame[lstCols].sum(axis=1)
    pdFrame.sort(columns='sum', inplace=True, ascending=False)
    return pdFrame

def read_mvd_data(str_source , lstSplitRegion=lst_exUSSR_nr):
    '''read mvd data - tourism, work migration etc, by countries, only 2016'''
    df_mvd=pd.read_excel(str_source, sheetname=1, header=None, 
                     skiprows =13, index_col=0, 
                     names=['invitation', 'visa', 'reg_all', 'reg_location', 'reg_residence', 'base', 'tourism', 
                            'study', 'work', 'personal', 'other', 'reg_out', 'des_rvp', 'rvp', 'des_pmg', 'pmg', 
                            'get_citi', 'for_del']).dropna()
    df_mvd.index.name='Country'
    df_mvd.drop('for_del', inplace=True, axis=1)

    dEx=make_dict(df_mvd.index.tolist(), key='exUSSR', src_lst=lstSplitRegion)
    #print(dEx)
    df_mvd.reset_index(inplace=True)
    df_mvd['Country']=df_mvd['Country'].str.strip()

    df_mvd['AREA2']=df_mvd['Country'].map(dEx)
    df_mvd['AREA2'].fillna('FOREIGN', inplace=True)
    df_mvd['CountryEng']=df_mvd['Country'].map(make_translate_dict('coutries.txt'))

    ddd=df_mvd[['Country', 'CountryEng']].where(df_mvd['CountryEng'].isnull())
    d=df_mvd[ddd['Country'].notnull() & ddd['CountryEng'].isnull()].sum()
    d['Country']='Другие'
    d.name='Other'
    
    df_mvd.set_index('CountryEng', inplace=True)
    df_mvd=df_mvd.append(d)
    df_mvd.loc['Other', 'AREA2']='FOREIGN'
    return df_mvd.drop('CountryEng', axis=1)

#mvd=read_mvd_data(strInternalViewByCountry)
#print(mvd)