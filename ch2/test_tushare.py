import tushare as ts

# 读者的Tushare接口token
TOKEN = '*******************************************************'
# 需要读取行情的标的代码
TS_CODE = '600519.SH'
# 行情的起止日期
START_DATE = '20220701'
END_DATE = '20221010'

# 使用token初始化api
pro = ts.pro_api(TOKEN)
# 读取标的的日线数据
daily = pro.daily(ts_code=TS_CODE, start_date=START_DATE, end_date=END_DATE)
print(daily)
