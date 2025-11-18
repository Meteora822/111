from datetime import date
from sqlalchemy import Column, Integer, String, Float, Date, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Record(Base):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(10), nullable=False)  # 'income' or 'expense'
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)
    note = Column(String(200))

def get_engine(db_uri=None):
    """
    获取数据库引擎
    db_uri: 数据库连接字符串，如果不提供则从 config.py 读取
    """
    if db_uri is None:
        try:
            from config import Config
            db_uri = Config.SQLALCHEMY_DATABASE_URI
        except ImportError:
            # 如果没有配置文件，使用 SQLite
            db_uri = 'sqlite:///records.db'
    
    return create_engine(db_uri, echo=False, future=True, pool_pre_ping=True)

def get_session(engine):
    Session = sessionmaker(bind=engine, future=True)
    return Session()
