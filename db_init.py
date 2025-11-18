from datetime import date
from models import Base, Record, get_engine, get_session

def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    session = get_session(engine)
    # 插入一些示例数据
    if session.query(Record).count() == 0:
        sample = [
            Record(type='income', amount=5000, category='工资', date=date(2025,1,5), note='一月工资'),
            Record(type='expense', amount=50, category='餐饮', date=date(2025,1,6), note='午餐'),
            Record(type='expense', amount=100, category='交通', date=date(2025,1,7), note='地铁卡充值'),
            Record(type='expense', amount=200, category='购物', date=date(2025,1,10), note='买书'),
        ]
        session.add_all(sample)
        session.commit()
    session.close()

if __name__ == '__main__':
    init_db()
    print('初始化完成，数据库文件 records.db 已创建（如不存在）。')
