import os
import pandas as pd
import matplotlib.pyplot as plt
import pymysql
import matplotlib
from datetime import datetime
import matplotlib.dates as mdates
matplotlib.use('TkAgg')

startTime_str = input("시작 시간을 입력해주세요 (YYYY-MM-DD HH:MM:SS): ")
endTime_str = input("마감 시간을 입력해주세요 (YYYY-MM-DD HH:MM:SS): ")
print(startTime_str, endTime_str)

startTime = datetime.strptime(startTime_str, "%Y-%m-%d %H:%M")
endTime = datetime.strptime(endTime_str, "%Y-%m-%d %H:%M")

startTime = pd.to_datetime(startTime)
endTime = pd.to_datetime(endTime)

plt.rcParams['agg.path.chunksize'] = 200
plt.rcParams['path.simplify_threshold'] = 0.2
matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

# table connect
conn = pymysql.connect(host='xxx.xx.xxx.xxx', port=xxxx, user='root', passwd='xxxxxxxxxxxx',
                       db='space_edge', charset='utf8')
cur = conn.cursor()
conn2 = pymysql.connect(host='xxx.xx.xxx.xxx', port=xxxx, user='root', passwd='xxxxxxxxxxxx',
                        db='space_edge_history1', charset='utf8')
cur2 = conn2.cursor()

query1 = """SELECT ID,regdate,Occ FROM ai_outputdata_history WHERE ID = %s"""
query2 = """SELECT s_num, regdate, temp, humi, illuminance, co2, dust_pm_1, dust_pm_25, dust_pm_10, voc, in_room FROM env_history WHERE s_num = %s AND %s <= regdate AND regdate <= %s"""


# 디렉토리 설정
directory = 'C:\\Uers\\UserPc\\Downloads'
if not os.path.exists(directory):
    os.makedirs(directory)

# sql에서 dvice데이터 불러오기
df_device = pd.read_sql_query('SELECT * FROM device', conn)
unique_s_nums = df_device['s_num'].unique()
# print(unique_s_nums)

# device데이터프레임에서 기계(s_num)별 위치를 저장한 데이터프레임 생성
latest_sid_rows = df_device.groupby('s_num')['sid'].idxmax()
result_df_device = df_device.loc[latest_sid_rows, ['s_num', 'name']]
print(result_df_device)

s_num_list = input("번호를 입력하세요 (여러 개의 번호는 스페이스바로 구분): ").split()
print("입력된 번호들:", s_num_list)

# sql에서 ai_outputdata_history데이터 불러오기
#df_ai_outputdata_history = pd.read_sql_query('SELECT ID,regdate,Occ FROM ai_outputdata_history', conn2)
cur2.execute(query1, s_num_list)
df_ai_outputdata_history = cur2.fetchall()
df_ai_outputdata_history = pd.DataFrame(df_ai_outputdata_history)
df_ai_outputdata_history[1] = df_ai_outputdata_history[1].dt.strftime('%Y-%m-%d %H:%M')
df_ai_outputdata_history[1] = pd.to_datetime(df_ai_outputdata_history[1], format='%Y-%m-%d %H:%M')
df_ai_outputdata_history.rename(columns={0: 's_num', 1:'regdate', 2:'Occ'}, inplace=True)
print("df_ai_outputdata_history head")
print(df_ai_outputdata_history.head())

# sql에서 env_history데이터 불러오기
#df_env_history_s = pd.read_sql_query('SELECT s_num, regdate, temp, humi, illuminance, co2, dust_pm_1, dust_pm_25, dust_pm_10, voc, in_room FROM env_history', conn2)
cur2.execute(query2, (s_num_list, startTime_str, endTime_str))
df_env_history_s = cur2.fetchall()
df_env_history_s = pd.DataFrame(df_env_history_s)
df_env_history_s[1] = df_env_history_s[1].dt.strftime('%Y-%m-%d %H:%M')
df_env_history_s[1] = pd.to_datetime(df_env_history_s[1], format='%Y-%m-%d %H:%M')
df_env_history_s.rename(columns={0: 's_num', 1:'regdate', 2:'temp', 3:'humi', 4:'illuminance', 5:'co2', 6:'dust_pm_1', 7:'dust_pm_25', 8:'dust_pm_10', 9: 'voc', 10:'in_room'}, inplace=True)
print("df_env_history_s head")
print(df_env_history_s.head())

merge_data = df_env_history_s.merge(df_ai_outputdata_history, on=["s_num", "regdate"], how='left')
# print(merge_data.head())
# print(merge_data.shape)

# 입력한 날짜 및 시간 데이터만 출력
merge_data['regdate'] = pd.to_datetime(merge_data['regdate'])
extracted_data = merge_data
# print(extracted_data.head())

filtered_data = extracted_data[extracted_data['s_num'].isin(s_num_list)]
groups = filtered_data.groupby('s_num')

for s_num, group in groups:
    location = result_df_device.loc[result_df_device['s_num'] == s_num]['name'].values[0]
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange', 'purple']

    ax1 = plt.subplot(3, 3, 1)
    ax1.plot(group['regdate'], group['temp'], color=colors[0])
    plt.title('Temperature')
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H'))

    ax2 = plt.subplot(3, 3, 2)
    ax2.plot(group['regdate'], group['humi'], color=colors[1])
    plt.title('Humidity')
    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H'))

    ax3 = plt.subplot(3, 3, 3)
    ax3.plot(group['regdate'], group['co2'], color=colors[2])
    plt.title('$CO_2$')
    ax3.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H'))

    ax4 = plt.subplot(3, 3, 4)
    ax4.plot(group['regdate'], group['dust_pm_1'], color=colors[3])
    plt.title('dust_pm_1')
    ax4.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%H'))

    ax5 = plt.subplot(3, 3, 5)
    ax5.plot(group['regdate'], group['dust_pm_25'], color=colors[4])
    plt.title('dust_pm_25')
    ax5.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax5.xaxis.set_major_formatter(mdates.DateFormatter('%H'))

    ax6 = plt.subplot(3, 3, 6)
    ax6.plot(group['regdate'], group['dust_pm_10'], color=colors[5])
    plt.title('dust_pm_10')
    ax6.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax6.xaxis.set_major_formatter(mdates.DateFormatter('%H'))

    ax7 = plt.subplot(3, 3, 7)
    ax7.plot(group['regdate'], group['illuminance'], color=colors[6])
    plt.title('Illuminance')
    ax7.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax7.xaxis.set_major_formatter(mdates.DateFormatter('%H'))

    ax8 = plt.subplot(3, 3, 8)
    ax8.plot(group['regdate'], group['voc'], color=colors[7])
    plt.title('VOC')
    ax8.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax8.xaxis.set_major_formatter(mdates.DateFormatter('%H'))

    ax9 = plt.subplot(3, 3, 9)
    ax9.plot(group['regdate'], group['Occ'], color=colors[8])
    plt.title('Occupancy')
    ax9.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax9.xaxis.set_major_formatter(mdates.DateFormatter('%H'))

    plt.suptitle(str(s_num) + '- (' + str(startTime_str) + '~' + str(endTime_str) + ') -' + str(location))
    plt.tight_layout()
    plt.show()