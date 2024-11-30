import json

# 初始化python字典
py_dict = {'message': 'json is brilliant!', 'version': 1.14, 'info': 'python dict'}

# 使用dump方法向文件写入python字典
with open('py_dict.json', 'w', encoding='utf8') as f:
    json.dump(py_dict, f)

# 使用dumps（dump+string）将字典值转换为对应字符串
dict2str = json.dumps(py_dict)
print(dict2str)
# ====================================================================
# 打开并读取json文件
with open('py_dict.json', 'r', encoding='utf8') as f:
    load_json_file = json.load(f)

# 初始化一个JSON格式的字符串
json_like_str = r'{"message": "json is brilliant!", "version": 1.14, "info": "json-like string"}'
# 从字符串中读取数据
load_json_str = json.loads(json_like_str)

# 打印从文件中读取的数据
print(load_json_file)
# 打印从字符串读取的数据
print(load_json_str)
