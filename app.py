import numpy as np
import pandas as pd
import requests
import datetime
import re
import time
from tkinter import *
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import matplotlib.pyplot as plt
from pandastable import Table, TableModel
import matplotlib as mpl
import random
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

request_times = 0
with open('../Date_Setting.txt',mode='r') as f:
    settings = f.readlines()

settings = [i.replace('\n',"").split(":")[1] for i in settings]

START = settings[0]
END = settings[1]
BATCH = settings[2]

try:
    START = pd.to_datetime(START).date()
except:
    pass

try:
    END = pd.to_datetime(END).date()
except:
    pass

if BATCH=='T' or BATCH=='TRUE' or BATCH=='True':
    if type(END) == pd._libs.tslibs.nattype.NaTType:
        END = datetime.date.today()
    else:
        pass
    
    print('啟動批次下載，期間為 : {}   至  {}'.format(START.strftime('%Y/%m/%d'), END.strftime('%Y/%m/%d')))

    date_range = []
    add_day = START
    Range_END = END+pd.tseries.offsets.MonthEnd(1)
    Range_END = Range_END.date()

    while add_day < Range_END:
        date_range.append(add_day)
        add_day = (add_day+pd.tseries.offsets.MonthEnd(1)).date()

    date_range.append(END)

    Data = pd.DataFrame()

    for i in range(len(date_range)-1):
        
        DATA_START = date_range[i]
        DATA_END = date_range[i+1]
        print(DATA_START,   DATA_END)
        
        try_count=1
        while try_count<10:
            try:
                print("第 {} 次嘗試下載".format(try_count))
                res = requests.get('https://www.twse.com.tw/SBL/t13sa710?response=csv&startDate={}&endDate={}&stockNo=&tradeType='.format(DATA_START.strftime('%Y%m%d'), DATA_END.strftime('%Y%m%d')))
                
                time.sleep(3)
                
                a = res.text.split('\r\n')[1:-6] #原始文字清洗，清除首行及表尾說明語句
                b = [a.replace('=', "") for a in a]  #非個股其證券代號名稱前會有等號，予以刪除
                c = [c.split('","') for c in b] #每一列分割欄位

                df = pd.DataFrame(c[1:], columns=c[0])

                df.columns = [col.replace('"', "").replace(",","") for col in df.columns]
                df = df.applymap(lambda x:str(x).replace('"', "").replace(",", ""))
                patterns = re.compile(u"[\u4e00-\u9fa5-A-z0-9&]+")

                pattern = r"^[0-9A-z]*"
                df['證券代號'] = df.證券代號名稱.apply(lambda x:re.findall(patterns,x)[0])
                df['證券名稱'] = df.證券代號名稱.apply(lambda x:re.findall(patterns,x)[1])

                df['成交日期'] = df.成交日期.apply(lambda x:int(re.sub(r'年|月|日', '', x))+19110000)
                df['成交日期'] = pd.to_datetime(df['成交日期'], format='%Y%m%d')
                df['成交日期'] = df['成交日期'].apply(lambda x:x.date())
                df['約定還券日期'] = df.約定還券日期.apply(lambda x:int(re.sub(r'年|月|日', '', x))+19110000)
                df['約定還券日期'] = pd.to_datetime(df['約定還券日期'], format='%Y%m%d')
                df['約定還券日期'] = df['約定還券日期'].apply(lambda x:x.date())

                df = df[['成交日期',
                '證券代號', 
                '證券名稱', 
                '交易方式', 
                '成交數量(交易單位)', 
                '成交費率', 
                '成交日收盤價', 
                '約定還券日期',
                '約定借券天數', 
                '費率異動'
               ]]

                df.成交費率 = df.成交費率.astype(float)
                df['成交數量(交易單位)'] = df['成交數量(交易單位)'].astype(int)
                
                print("下載成功")
                try_count=10
                Data = Data.append(df)

            except:
                print("下載失敗")
                try_count+=1
                
    print("全部資料下載完成")
    df = Data.drop_duplicates()
    print("儲存資料")
    df.to_csv("../最近一次批次抓取資料.csv", index=False, encoding="utf-8_sig")
    

while (request_times < 5) & (BATCH==""):
    try:
        print("抓取資料")
        
        today = datetime.date.today()

        if type(START) == pd._libs.tslibs.nattype.NaTType:
            print("無定義日期，預設使用上個月為開始時間")
            last_month_date = (today - pd.tseries.offsets.MonthEnd(1)).replace(day=1).date()

            res = requests.get('https://www.twse.com.tw/SBL/t13sa710?response=csv&startDate={}&endDate={}&stockNo=&tradeType='.format(last_month_date.strftime('%Y%m%d'), today.strftime('%Y%m%d')))

        elif (type(START) == datetime.date) & (type(END) == datetime.date):
            print("定義開始與結束日期為: {} 到 {}".format(START.strftime('%Y%m%d'), END.strftime('%Y%m%d')))

            res = requests.get('https://www.twse.com.tw/SBL/t13sa710?response=csv&startDate={}&endDate={}&stockNo=&tradeType='.format(START.strftime('%Y%m%d'), END.strftime('%Y%m%d')))

        else:
            print("定義開始日期為: {}".format(START.strftime('%Y%m%d')))

            res = requests.get('https://www.twse.com.tw/SBL/t13sa710?response=csv&startDate={}&endDate={}&stockNo=&tradeType='.format(START.strftime('%Y%m%d'), today.strftime('%Y%m%d')))

        
        #--------------清洗資料--------------
        a = res.text.split('\r\n')[1:-6] #原始文字清洗，清除首行及表尾說明語句
        b = [a.replace('=', "") for a in a]  #非個股其證券代號名稱前會有等號，予以刪除
        c = [c.split('","') for c in b] #每一列分割欄位
        
        df = pd.DataFrame(c[1:], columns=c[0])
        
        df.columns = [col.replace('"', "").replace(",","") for col in df.columns]
        df = df.applymap(lambda x:str(x).replace('"', "").replace(",", ""))
        patterns = re.compile(u"[\u4e00-\u9fa5-A-z0-9&]+")
        
        pattern = r"^[0-9A-z]*"
        df['證券代號'] = df.證券代號名稱.apply(lambda x:re.findall(patterns,x)[0])
        df['證券名稱'] = df.證券代號名稱.apply(lambda x:re.findall(patterns,x)[1])
        
        df['成交日期'] = df.成交日期.apply(lambda x:int(re.sub(r'年|月|日', '', x))+19110000)
        df['成交日期'] = pd.to_datetime(df['成交日期'], format='%Y%m%d')
        df['成交日期'] = df['成交日期'].apply(lambda x:x.date())
        df['約定還券日期'] = df.約定還券日期.apply(lambda x:int(re.sub(r'年|月|日', '', x))+19110000)
        df['約定還券日期'] = pd.to_datetime(df['約定還券日期'], format='%Y%m%d')
        df['約定還券日期'] = df['約定還券日期'].apply(lambda x:x.date())
        
        df = df[['成交日期',
        '證券代號', 
        '證券名稱', 
        '交易方式', 
        '成交數量(交易單位)', 
        '成交費率', 
        '成交日收盤價', 
        '約定還券日期',
        '約定借券天數', 
        '費率異動'
       ]]
        
        df.成交費率 = df.成交費率.astype(float)
        df['成交數量(交易單位)'] = df['成交數量(交易單位)'].astype(int)
        
        print("資料抓取成功")
        request_times = 5
        
    except:
        print("資料抓取失敗")
        time.sleep(3)
        request_times +=1

with open('../Core_Setting.txt',mode='r') as f:
    settings = f.readlines()

settings = [i.replace('\n',"").split(":")[1] for i in settings]

TABLE_WIDTH = float(settings[0])
TABLE_HEIGHT = float(settings[1])
PLOT_WIDTH = int(settings[2])
PLOT_HEIGHT = int(settings[3])


#Create the frame class and call my functions from inside the class
sns.set_style("darkgrid",{"font.sans-serif":['Microsoft JhengHei']})
mpl.rcParams['axes.unicode_minus'] = False


class UserInterface(Table):
    # Launch the df in a pandastable frame

    def handleCellEntry(self, row, col):
        super().handleCellEntry(row, col)
        print('changed:', row, col, "(TODO: update database)")
        return    

    def change_df_combo(self, event):
        #Responds to combobox, filter by 'Sec_type'
        global ui_df, refresh_plot
        combo_selection = str(combo_box.get())
        combo_selection1 = str(combo_box1.get())
        combo_selection2 = str(combo_box2.get())
        
        ui_df = pos_df.copy()
        
        if combo_selection == "選擇成交日期":
            pass
        else:
            ui_df = ui_df[pos_df.成交日期.apply(lambda x:str(x)) == combo_selection]
            
        if combo_selection1 == "選擇交易方式":
            pass
        else:
            ui_df = ui_df.query("交易方式 == @combo_selection1")
            
        if combo_selection2 == "選擇證券代號":
            pass
        else:
            ui_df = ui_df.query("證券代號 == @combo_selection2") 
        
        refresh_plot(event)
            
        self.updateModel(TableModel(ui_df))
        self.redraw()
        
    def change_df_combo1(self, event):
        #Responds to combobox, filter by 'Sec_type'
        global ui_df, refresh_plot
        combo_selection = str(combo_box.get())
        combo_selection1 = str(combo_box1.get())
        combo_selection2 = str(combo_box2.get())
        
        ui_df = pos_df.copy()
        
        if combo_selection == "選擇成交日期":
            pass
        else:
            ui_df = ui_df[pos_df.成交日期.apply(lambda x:str(x)) == combo_selection]
            
        if combo_selection1 == "選擇交易方式":
            pass
        else:
            ui_df = ui_df.query("交易方式 == @combo_selection1")
            
        if combo_selection2 == "選擇證券代號":
            pass
        else:
            ui_df = ui_df.query("證券代號 == @combo_selection2") 
            
        refresh_plot(event)
            
        self.updateModel(TableModel(ui_df))
        self.redraw()
        
    def change_df_combo2(self, event):
        global ui_df, refresh_plot
        #Responds to combobox, filter by 'Sec_type'
        combo_selection = str(combo_box.get())
        combo_selection1 = str(combo_box1.get())
        combo_selection2 = str(combo_box2.get())
        
        ui_df = pos_df.copy()
        
        if combo_selection == "選擇成交日期":
            pass
        else:
            ui_df = ui_df[pos_df.成交日期.apply(lambda x:str(x)) == combo_selection]
            
        if combo_selection1 == "選擇交易方式":
            pass
        else:
            ui_df = ui_df.query("交易方式 == @combo_selection1")
            
        if combo_selection2 == "選擇證券代號":
            pass
        else:
            ui_df = ui_df.query("證券代號 == @combo_selection2") 
            
        refresh_plot(event)

        self.updateModel(TableModel(ui_df))
        self.redraw()

        
def create_plot():
    # sns.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
#     sns.set_style("darkgrid",{"font.sans-serif":['Microsoft JhengHei']})
    # sns.set_style("darkgrid")
    
#     mpl.rcParams['axes.unicode_minus'] = False
    global PLOT_WIDTH, PLOT_HEIGHT

    fig, ax = plt.subplots(3,1,figsize=(PLOT_WIDTH, PLOT_HEIGHT))
    plt.subplots_adjust(hspace=0.4)

    sns.lineplot(y=ui_df.成交費率, x=list(range(len(ui_df.成交費率))), ax=ax[0])
    sns.lineplot(y=ui_df['成交數量(交易單位)'], x=list(range(len(ui_df.成交費率))), ax=ax[1])
    sns.histplot(x='成交費率', hue='交易方式', kde=False, stat='count', data=ui_df, ax=ax[2])

    ax[0].set_title('借券費率變動趨勢(根據每筆資料)')
    ax[1].set_title('成交數量變動趨勢')
    ax[2].set_title('借券費率分配')

    
    return fig

    
def refresh_plot(event):
    global fig, canvas, ui_df, PLOT_WIDTH, PLOT_HEIGHT
    
    # sns.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
#     sns.set_style("darkgrid",{"font.sans-serif":['Microsoft JhengHei']})
    # sns.set_style("darkgrid")
#     mpl.rcParams['axes.unicode_minus'] = False
    
    
    fig, ax = plt.subplots(3,1,figsize=(PLOT_WIDTH, PLOT_HEIGHT))
    plt.subplots_adjust(hspace=0.4)

    sns.lineplot(y=ui_df.成交費率, x=list(range(len(ui_df.成交費率))), ax=ax[0])
    sns.lineplot(y=ui_df['成交數量(交易單位)'], x=list(range(len(ui_df.成交費率))), ax=ax[1])
    sns.histplot(x='成交費率', hue='交易方式', kde=False, stat='count', data=ui_df, ax=ax[2])

    ax[0].set_title('借券費率變動趨勢(根據每筆資料)')
    ax[1].set_title('成交數量變動趨勢')
    ax[2].set_title('借券費率分配')
    
    
    canvas.figure = fig
#     canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
#     canvas.get_tk_widget().grid(column=0, row=3, sticky=(NW),padx=5)

def save_table():
    global  ui_df
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    ui_df.to_csv("../{}.csv".format(timestamp), index=False, encoding="utf-8_sig")
    
    tk.messagebox.showinfo("儲存成功","檔名為 : {}.csv".format(timestamp))
    
    

    
pos_df = df
ui_df = pos_df

#Launch Tkinter basics
root = Tk()
root.title("借券費率")

mainframe = ttk.Frame(root, padding="3 3 3 3")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

f = Frame(mainframe)
f.grid(column=0, columnspan=3,row=1, sticky=(E, W))
screen_width = f.winfo_screenwidth() * TABLE_WIDTH
screen_height = f.winfo_screenheight() * TABLE_HEIGHT

ui = UserInterface(f, dataframe=pos_df, height = screen_height, width = screen_width, showtoolbar=True, editable=False)


#Combobox to filter df
combo_choices = ['選擇成交日期']+list(np.unique(df.成交日期))
choice = StringVar()
combo_box = ttk.Combobox(mainframe, textvariable=choice)
combo_box['values'] = combo_choices
combo_box.grid(column=0, row=0, sticky=(NW))
combo_box.set("選擇成交日期")
combo_box.bind('<<ComboboxSelected>>', ui.change_df_combo)
combo_box.columnconfigure(0, weight=1)
combo_box.rowconfigure(0, weight=1)

#Combobox to filter df
combo_choices1 = ['選擇交易方式']+list(np.unique(df.交易方式))
choice1 = StringVar()
combo_box1 = ttk.Combobox(mainframe, textvariable=choice1, )
combo_box1['values'] = combo_choices1
combo_box1.grid(column=0, row=0, sticky=(N))
combo_box1.set("選擇交易方式")
combo_box1.bind('<<ComboboxSelected>>', ui.change_df_combo1)

combo_choices2 = ['選擇證券代號']+list(np.unique(df.證券代號))
choice2 = StringVar()
combo_box2 = ttk.Combobox(mainframe, textvariable=choice2)
combo_box2['values'] = combo_choices2
combo_box2.grid(column=0, row=0, sticky=(NE))
combo_box2.set("選擇證券代號")
combo_box2.bind('<<ComboboxSelected>>', ui.change_df_combo2)

download_button = tk.Label(mainframe, text='           ' )
download_button.grid(column=1, row=0,  sticky=(N))

download_button = tk.Button(mainframe, text='儲存當前表格資料', command=save_table )
download_button.grid(column=2, row=0,  sticky=(NE))


fig = create_plot()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().grid(column=4, row=0, rowspan=3)


ui.show()

root.mainloop()
root.quit()