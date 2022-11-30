from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config

Base = declarative_base()


def create_dbsession():
    engine = create_engine(f"postgresql://{config.user}:{config.password}@{config.host}/{config.db}",
                           echo=True)
    Base.metadata.create_all(engine)
    Session_local = sessionmaker(bind=engine)
    return Session_local()
