import numpy as np
import pandas as pd
import requests
import datetime
import re
import time
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
import seaborn as sns
from pandastable import Table, TableModel
from fake_useragent import UserAgent
import random
import mplcursors
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
####################################################
# 抓取外部設定檔
#--------------------------------------
# Date Setting
try:
    with open('../Date_Setting.txt',mode='r', encoding='utf-8') as f:
        date_settings = f.readlines()
except:
    print('未定義Date_Setting    由系統建立預設值設定檔')
    with open("../Date_Setting.txt", "a") as f:
        f.write("START:\nEND:\nBATCH:\nHISTORICAL_DATA:")
    with open('../Date_Setting.txt',mode='r') as f:
        date_settings = f.readlines()

date_settings = [i.replace('\n',"").split(":")[1] for i in date_settings]

START = date_settings[0]
END = date_settings[1]
BATCH = date_settings[2]
HISTORICAL_DATA = date_settings[3]

# Core Setting
try:
    with open('../Core_Setting.txt',mode='r', encoding='utf-8') as f:
        core_settings = f.readlines()
except:
    print('未定義Core_Setting    由系統建立預設值設定檔')
    with open("../Core_Setting.txt", "a") as f:
        f.write("TABLE_WIDTH:0.4\nTABLE_HEIGHT:0.5\nPLOT_WIDTH:8\nPLOT_HEIGHT:6")
    with open('../Core_Setting.txt',mode='r') as f:
        core_settings = f.readlines()

core_settings = [i.replace('\n',"").split(":")[1] for i in core_settings]

TABLE_WIDTH = float(core_settings[0])
TABLE_HEIGHT = float(core_settings[1])
PLOT_WIDTH = int(core_settings[2])
PLOT_HEIGHT = int(core_settings[3])

####################################################

####################################################
# 爬取資料
#-----------------------------------------------
request_times = 0  # 試誤次數
df = None
OMIT_DOWNLOAD = None

#檢查是否有在Date Setting傳入參數
try:
    START = pd.to_datetime(START).date()
except:
    pass

try:
    END = pd.to_datetime(END).date()
except:
    pass

try:
    df = pd.read_csv("../{}".format(HISTORICAL_DATA))

except:
    OMIT_DOWNLOAD = None

if type(df) == pd.core.frame.DataFrame:
    OMIT_DOWNLOAD = True

if OMIT_DOWNLOAD == True:
    print('使用保存的歷史資料：{}'.format(HISTORICAL_DATA))

#設定Header，讓爬蟲比較不容易被擋

def set_header_user_agent():
    user_agent = UserAgent()
    return user_agent.random

user_agent = set_header_user_agent()

#依照Date Setting參數設定，調整資料取得方式
#分成三大部分：
# 1.如果上面的歷史資料有設定，就會跳過下面的爬取資料部分
# 2.如果有設定批次抓取，則會用批次抓取的程式區塊 (Batch=T)
# 3.如果沒設定批次抓取，則會直接抓取
if (BATCH=='T' or BATCH=='TRUE' or BATCH=='True') & (OMIT_DOWNLOAD != True):

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
                user_agent = set_header_user_agent()
                res = requests.get('https://www.twse.com.tw/SBL/t13sa710?response=csv&startDate={}&endDate={}&stockNo=&tradeType='.format(DATA_START.strftime('%Y%m%d'), DATA_END.strftime('%Y%m%d')), headers={ 'user-agent': user_agent})
                
                time.sleep(random.randint(3, 6))
                
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
    

while (request_times < 5) & (BATCH=="") & (OMIT_DOWNLOAD != True):
    try:
        print("抓取資料")
        
        today = datetime.date.today()

        if type(START) == pd._libs.tslibs.nattype.NaTType:
            print("無定義日期，預設使用上個月為開始時間")
            last_month_date = (today - pd.tseries.offsets.MonthEnd(1)).replace(day=1).date()

            res = requests.get('https://www.twse.com.tw/SBL/t13sa710?response=csv&startDate={}&endDate={}&stockNo=&tradeType='.format(last_month_date.strftime('%Y%m%d'), today.strftime('%Y%m%d')), headers={ 'user-agent': user_agent})

        elif (type(START) == datetime.date) & (type(END) == datetime.date):
            print("定義開始與結束日期為: {} 到 {}".format(START.strftime('%Y%m%d'), END.strftime('%Y%m%d')))

            res = requests.get('https://www.twse.com.tw/SBL/t13sa710?response=csv&startDate={}&endDate={}&stockNo=&tradeType='.format(START.strftime('%Y%m%d'), END.strftime('%Y%m%d')), headers={ 'user-agent': user_agent})

        else:
            print("定義開始日期為: {}".format(START.strftime('%Y%m%d')))

            res = requests.get('https://www.twse.com.tw/SBL/t13sa710?response=csv&startDate={}&endDate={}&stockNo=&tradeType='.format(START.strftime('%Y%m%d'), today.strftime('%Y%m%d')), headers={ 'user-agent': user_agent})

        
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
        time.sleep(random.randint(3, 9))
        request_times +=1

#-----------------------------------------------
# 爬取資料
########################################


########################################
#圖形化介面
#-----------------------------------------------
#Create the frame class and call my functions from inside the class
sns.set_style("darkgrid",{"font.sans-serif":['Microsoft JhengHei']})
mpl.rcParams['axes.unicode_minus'] = False


class UserInterface(Table):
    # Launch the df in a pandastable frame

    def handleCellEntry(self, row, col):
        super().handleCellEntry(row, col)
        print('changed:', row, col, "(TODO: update database)")
        return 0

    def change_df_combo(self, event):
        #Responds to combobox, filter by 'Sec_type'
        global ui_df, refresh_plot
        combo_selection = str(combo_box.get())
        combo_selection1 = str(combo_box1.get())
        combo_selection2 = str(combo_box2.get())
        combo_selection3 = str(combo_box3.get())
        
        ui_df = pos_df.copy()
        
        if combo_selection == "選擇開始日期":
            pass
        else:
            start_index = min(ui_df[pos_df.成交日期.apply(lambda x:str(x)) == combo_selection].index)
            ui_df = ui_df.loc[start_index:]
        
        if combo_selection3 == "選擇結束日期":
                pass
        else:
            end_index = min(ui_df[pos_df.成交日期.apply(lambda x:str(x)) == combo_selection3].index)
            ui_df = ui_df.loc[:end_index]
            
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
        combo_selection3 = str(combo_box3.get())
        
        ui_df = pos_df.copy()
        
        if combo_selection == "選擇開始日期":
            pass
        else:
            start_index = min(ui_df[pos_df.成交日期.apply(lambda x:str(x)) == combo_selection].index)
            ui_df = ui_df.loc[start_index:]
        
        if combo_selection3 == "選擇結束日期":
                pass
        else:
            end_index = min(ui_df[pos_df.成交日期.apply(lambda x:str(x)) == combo_selection3].index)
            ui_df = ui_df.loc[:end_index]
            
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
        #Responds to combobox, filter by 'Sec_type'
        global ui_df, refresh_plot
        combo_selection = str(combo_box.get())
        combo_selection1 = str(combo_box1.get())
        combo_selection2 = str(combo_box2.get())
        combo_selection3 = str(combo_box3.get())
        
        ui_df = pos_df.copy()
        
        if combo_selection == "選擇開始日期":
            pass
        else:
            start_index = min(ui_df[pos_df.成交日期.apply(lambda x:str(x)) == combo_selection].index)
            ui_df = ui_df.loc[start_index:]
        
        if combo_selection3 == "選擇結束日期":
                pass
        else:
            end_index = min(ui_df[pos_df.成交日期.apply(lambda x:str(x)) == combo_selection3].index)
            ui_df = ui_df.loc[:end_index]
            
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
    
    def change_df_combo3(self, event):
        #Responds to combobox, filter by 'Sec_type'
        global ui_df, refresh_plot
        combo_selection = str(combo_box.get())
        combo_selection1 = str(combo_box1.get())
        combo_selection2 = str(combo_box2.get())
        combo_selection3 = str(combo_box3.get())
        
        ui_df = pos_df.copy()
        
        if combo_selection == "選擇開始日期":
            pass
        else:
            start_index = min(ui_df[pos_df.成交日期.apply(lambda x:str(x)) == combo_selection].index)
            ui_df = ui_df.loc[start_index:]
        
        if combo_selection3 == "選擇結束日期":
                pass
        else:
            end_index = min(ui_df[pos_df.成交日期.apply(lambda x:str(x)) == combo_selection3].index)
            ui_df = ui_df.loc[:end_index]
            
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
    global PLOT_WIDTH, PLOT_HEIGHT, dot1, dot2
    
    fig, ax = plt.subplots(3,1,figsize=(PLOT_WIDTH, PLOT_HEIGHT))
    plt.subplots_adjust(hspace=0.4)

    ax[0].plot(list(range(len(ui_df.成交費率))), ui_df.成交費率)
    dot1 = ax[0].scatter(list(range(len(ui_df.成交費率))), ui_df.成交費率, s=1)
    ax[1].plot(list(range(len(ui_df.成交費率))), ui_df['成交數量(交易單位)'])
    dot2 = ax[1].scatter(list(range(len(ui_df.成交費率))), ui_df['成交數量(交易單位)'], s=1)
    sns.histplot(x='成交費率', hue='交易方式', kde=False, stat='count', data=ui_df, ax=ax[2])
    ax[0].set_title('借券費率變動趨勢(根據每筆資料)')
    ax[1].set_title('成交數量變動趨勢')
    ax[2].set_title('借券費率分配')

    return fig, ax
    
def refresh_plot(event):
    global fig, ax, canvas, ui_df, PLOT_WIDTH, PLOT_HEIGHT, cursor
    
    ax[0].clear()
    ax[1].clear()
    ax[2].clear()
    ax[0].plot(list(range(len(ui_df.成交費率))), ui_df.成交費率)

    dot1 = ax[0].scatter(list(range(len(ui_df.成交費率))), ui_df.成交費率, s=1)
    ax[1].plot(list(range(len(ui_df.成交費率))), ui_df['成交數量(交易單位)'])
    dot2 = ax[1].scatter(list(range(len(ui_df.成交費率))), ui_df['成交數量(交易單位)'], s=1)
    sns.histplot(x='成交費率', hue='交易方式', kde=False, stat='count', data=ui_df, ax=ax[2])

    ax[0].set_title('借券費率變動趨勢(根據每筆資料)')
    ax[1].set_title('成交數量變動趨勢')
    ax[2].set_title('借券費率分配')
    
    annot_table = ui_df.reset_index()
    canvas.figure = fig
    canvas.draw()

    cursor = mplcursors.cursor([dot1,dot2], highlight=True).connect(
        "add",
        lambda sel: sel.annotation.set_text(
            f'資料序列 : {int(sel.target[0])+1}\n成交日期 : {annot_table.成交日期[sel.target[0]]}\n證券名稱 : {annot_table.證券名稱[sel.target[0]]}\n交易方式 : {annot_table.交易方式[sel.target[0]]}\n成交數量 : {annot_table["成交數量(交易單位)"][sel.target[0]]}\n成交費率 : {annot_table.成交費率[sel.target[0]]}'
        ))

    cursor1 = mplcursors.cursor([ax[2]]).connect(
        "add",
        lambda sel: sel.annotation.set_text(f'Counts : {int(sel.target[1])}'))


def save_table():
    global  ui_df
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    ui_df.to_csv("../{}.csv".format(timestamp), index=False, encoding="utf-8_sig")
    
    tk.messagebox.showinfo("儲存成功","檔名為 : {}.csv".format(timestamp))
    

def load_table():
    global  ui_df, pos_df, combo_choices, combo_choices1, combo_choices2, combo_choices3, combo_box, combo_box1, combo_box2, combo_box3, combo_box, combo_box1, combo_box2, combo_box3
    
    csv_file_path = askopenfilename()
    
    df = pd.read_csv(csv_file_path)
    pos_df = df.copy()
    ui_df = df.copy()
    combo_choices = ['選擇開始日期']+list(np.unique(df.成交日期))
    combo_choices1 = ['選擇交易方式']+list(np.unique(df.交易方式))
    combo_choices2 = ['選擇證券代號']+list(np.unique(df.證券代號))
    combo_choices3 = ['選擇結束日期']+list(np.unique(df.成交日期))
    combo_box['values'] = combo_choices
    combo_box1['values'] = combo_choices1
    combo_box2['values'] = combo_choices2
    combo_box3['values'] = combo_choices3
    combo_box.set("選擇開始日期")
    combo_box1.set("選擇交易方式")
    combo_box2.set("選擇證券代號")
    combo_box3.set("選擇結束日期")
    
    

    
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
f.grid(column=0, columnspan=3,row=2, sticky=(E, W))
screen_width = f.winfo_screenwidth() * TABLE_WIDTH
screen_height = f.winfo_screenheight() * TABLE_HEIGHT

ui = UserInterface(f, dataframe=pos_df, height = screen_height, width = screen_width, showtoolbar=True, editable=False)


#Combobox to filter df
combo_choices = ['選擇開始日期']+list(np.unique(df.成交日期))
choice = StringVar()
combo_box = ttk.Combobox(mainframe, textvariable=choice)
combo_box['values'] = combo_choices
combo_box.grid(column=0, row=0, sticky=(NW))
combo_box.set("選擇開始日期")
combo_box.bind('<<ComboboxSelected>>', ui.change_df_combo)
combo_box.columnconfigure(0, weight=1)
combo_box.rowconfigure(0, weight=1)


combo_choices1 = ['選擇交易方式']+list(np.unique(df.交易方式))
choice1 = StringVar()
combo_box1 = ttk.Combobox(mainframe, textvariable=choice1, )
combo_box1['values'] = combo_choices1
combo_box1.grid(column=0, row=1, sticky=(NW))
combo_box1.set("選擇交易方式")
combo_box1.bind('<<ComboboxSelected>>', ui.change_df_combo1)

combo_choices2 = ['選擇證券代號']+list(np.unique(df.證券代號))
choice2 = StringVar()
combo_box2 = ttk.Combobox(mainframe, textvariable=choice2)
combo_box2['values'] = combo_choices2
combo_box2.grid(column=0, row=1, sticky=(NE))
combo_box2.set("選擇證券代號")
combo_box2.bind('<<ComboboxSelected>>', ui.change_df_combo2)


combo_choices3 = ['選擇結束日期']+list(np.unique(df.成交日期))
choice3 = StringVar()
combo_box3 = ttk.Combobox(mainframe, textvariable=choice3)
combo_box3['values'] = combo_choices3
combo_box3.grid(column=0, row=0, sticky=(NE))
combo_box3.set("選擇結束日期")
combo_box3.bind('<<ComboboxSelected>>', ui.change_df_combo3)
combo_box3.columnconfigure(0, weight=1)
combo_box3.rowconfigure(0, weight=1)


download_button = tk.Button(mainframe, text='儲存當前表格資料', command=save_table )
download_button.grid(column=2, row=0,  sticky=(NE))

reload_button = tk.Button(mainframe, text='讀取表格資料', command=load_table )
reload_button.grid(column=2, row=1,  sticky=(NE))

fig, ax = create_plot()
canvas = FigureCanvasTkAgg(fig, master=root)

cursor = mplcursors.cursor([dot1,dot2], highlight=True).connect(
    "add",
    lambda sel: sel.annotation.set_text(
        f'資料序列 : {int(sel.target[0])+1}\n成交日期 : {ui_df.成交日期[sel.target[0]]}\n證券名稱 : {ui_df.證券名稱[sel.target[0]]}\n交易方式 : {ui_df.交易方式[sel.target[0]]}\n成交數量 : {ui_df["成交數量(交易單位)"][sel.target[0]]}\n成交費率 : {ui_df.成交費率[sel.target[0]]}'
    ))

cursor1 = mplcursors.cursor([ax[2]]).connect(
    "add",
    lambda sel: sel.annotation.set_text(f'Counts : {int(sel.target[1])}'))


canvas.draw()
canvas.get_tk_widget().grid(column=4, row=0, rowspan=3)



toolbarFrame = Frame(master=root)
toolbarFrame.grid(row=22,column=4, sticky=(NW))
toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
toolbar.update()


ui.show()
root.mainloop()

root.quit()