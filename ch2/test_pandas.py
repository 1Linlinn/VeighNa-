import pandas as pd

file_name = 'num_csv.csv'
csv_file = pd.read_csv(file_name)
print(csv_file)

# =====================================================
csv_file_wo_header = pd.read_csv(file_name, header=None)
print(csv_file_wo_header)

# =====================================================
csv_file_values = pd.read_csv(file_name).values
print(csv_file_values)

# =====================================================
file_name = 'num_excel.xlsx'
# 可以通过sheet名或者sheet的索引进行访问（'Sheet1' == 0，'Sheet2' == 1）
excel_file = pd.read_excel(file_name, 0)
print(excel_file)

# =====================================================
file_name = 'num_json.json'
# index -> [index], columns -> [columns], data -> [values]
json_file = pd.read_json(file_name, orient='split')
print(json_file)

# =====================================================
print(csv_file.iloc[0])

# =====================================================
# 方法1
print(csv_file['first'])
# 方法2
print(csv_file.loc[:, 'first'])

# =====================================================
# axis=1表示对行做操作
print(csv_file.max(axis=1))
# axis=0表示对列做操作，默认axis为0
print(csv_file.min(axis=0))
# 先取出列的平均值，接着再求一次列均值的均值即为整个DataFrame的均值
print(csv_file.mean().mean())

# =====================================================
# 插入一条所有数据为NaN的记录
csv_file_with_na = csv_file.reindex([0, 1, 2])
print(csv_file_with_na)
# 查看NaN在DataFrame中的位置
print(csv_file_with_na.isna())
# 使用每一列的平均值填入该列所有NaN的位置
print(csv_file_with_na.fillna(csv_file_with_na.mean(axis=0)))
# 在所有NaN的位置填入0
print(csv_file_with_na.fillna(0))
# 在所有NaN的位置填入"Missing"字段
print(csv_file_with_na.fillna('Missing'))
# 丢弃DataFrame中含有NaN的行
print(csv_file_with_na.dropna(axis=0))
# 丢弃DataFrame中含有NaN的列
print(csv_file_with_na.dropna(axis=1))
