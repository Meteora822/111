"""
MySQL 数据库初始化脚本
使用前请确保：
1. MySQL 服务已启动
2. 修改 config.py 中的数据库连接信息
3. 创建数据库（可选，脚本会自动创建）
"""
import pymysql
from config import Config
from models import Base, Record, get_engine, get_session
from datetime import date

def create_database():
    """创建数据库（如果不存在）"""
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD
        )
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✓ 数据库 '{Config.MYSQL_DATABASE}' 已创建或已存在")
        connection.close()
    except Exception as e:
        print(f"✗ 创建数据库失败: {e}")
        print("\n请检查：")
        print("1. MySQL 服务是否已启动")
        print("2. config.py 中的用户名和密码是否正确")
        print("3. 用户是否有创建数据库的权限")
        raise

def init_tables():
    """创建表结构"""
    try:
        engine = get_engine()
        Base.metadata.create_all(engine)
        print("✓ 数据表已创建")
        return engine
    except Exception as e:
        print(f"✗ 创建表失败: {e}")
        raise

def insert_sample_data(engine):
    """插入示例数据"""
    try:
        session = get_session(engine)
        if session.query(Record).count() == 0:
            sample = [
                Record(type='income', amount=5000, category='工资', date=date(2025,1,5), note='一月工资'),
                Record(type='expense', amount=50, category='餐饮', date=date(2025,1,6), note='午餐'),
                Record(type='expense', amount=100, category='交通', date=date(2025,1,7), note='地铁卡充值'),
                Record(type='expense', amount=200, category='购物', date=date(2025,1,10), note='买书'),
                Record(type='income', amount=300, category='兼职', date=date(2025,1,15), note='周末兼职'),
            ]
            session.add_all(sample)
            session.commit()
            print(f"✓ 已插入 {len(sample)} 条示例数据")
        else:
            print("✓ 数据库已有数据，跳过插入示例")
        session.close()
    except Exception as e:
        print(f"✗ 插入数据失败: {e}")
        raise

def main():
    print("=" * 60)
    print("MySQL 数据库初始化")
    print("=" * 60)
    print(f"\n连接信息：")
    print(f"  主机: {Config.MYSQL_HOST}:{Config.MYSQL_PORT}")
    print(f"  用户: {Config.MYSQL_USER}")
    print(f"  数据库: {Config.MYSQL_DATABASE}")
    print("\n开始初始化...\n")
    
    try:
        # 1. 创建数据库
        create_database()
        
        # 2. 创建表
        engine = init_tables()
        
        # 3. 插入示例数据
        insert_sample_data(engine)
        
        print("\n" + "=" * 60)
        print("✓ 初始化完成！现在可以运行 python app.py 启动应用")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ 初始化失败，请检查错误信息")
        print("=" * 60)
        return False
    
    return True

if __name__ == '__main__':
    main()
