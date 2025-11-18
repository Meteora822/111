"""
数据库配置文件
根据您的 MySQL 设置修改以下参数
"""
import os

class Config:
    # MySQL 数据库配置
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '1234')  # 修改为您的 MySQL 密码
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'accounting_db')
    
    # SQLAlchemy 配置
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # 设为 True 可查看 SQL 语句

# 使用 SQLite 的备用配置（如果不想用 MySQL）
class SQLiteConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///records.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
