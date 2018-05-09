from datetime import datetime
from sqlalchemy import Column, String, create_engine, Integer, ForeignKey, Boolean, DateTime, Enum, Table, Text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(
    "mysql+pymysql://root:xin123456@127.0.0.1/bw_admin?charset=utf8")
Base = declarative_base()
DB_Session = sessionmaker(bind=engine)
session = DB_Session()


class BaseModel(object):
    create_time = Column(DateTime, default=datetime.now())
    update_time = Column(DateTime, default=datetime.now(), onupdate=datetime.now())


class ZhData(BaseModel, Base):  # u
    __tablename__ = "cai_nei_stock"
    id = Column(Integer, primary_key=True)
    name = Column(String(10))
    code = Column(String(10))
    times = Column(String(10))
    v_num = Column(Integer)
    version = Column(String(100))
    reason = Column(String(100))
    strength = Column(String(5))
    article_id = Column(Integer, index=True)


class CaiData(BaseModel, Base):  # r
    __tablename__ = "cai_nei_data"
    id = Column(Integer, primary_key=True)
    types = Column(Integer, index=True)  # 类型
    title = Column(String(100))  # 标题
    source = Column(String(21), nullable=False)  # 来源
    published_time = Column(String(20), nullable=True)  # 出版时间
    reads = Column(Integer, nullable=True)
    article_id = Column(Integer, index=True)
    body = Column(Text, nullable=True)


class HelpData(BaseModel, Base):
    __tablename__ = "b_help_data"
    id = Column(Integer, primary_key=True)
    ids = Column(Integer)
    body = Column(Text, nullable=True)


class ZhongData(BaseModel, Base):
    __tablename__ = "z_jin_data"
    ids = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(String(100))  # # 标题
    time = Column(String(20))  # # 时间
    reads = Column(Integer)  # # 阅读量
    author = Column(String(15))  # 作者
    con = Column(Text, nullable=True)  # 内容
