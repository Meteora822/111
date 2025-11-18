# 简易在线记账本

这是一个轻量级的在线记账示例应用，基于 Flask + SQLite，实现了收支记录的增删改查、按时间/分类查询、以及简单的图表展示。

快速运行：

1. 创建并激活虚拟环境（Windows PowerShell）：

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python db_init.py
python app.py
```

2. 在浏览器打开 `http://127.0.0.1:5000/`。

文件说明：
- `app.py`：Flask 应用主入口。
- `models.py`：数据库模型。
- `db_init.py`：初始化数据库并插入示例数据。
- `templates/`：前端 HTML 模板。
- `static/`：前端 JS。
