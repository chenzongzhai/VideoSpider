# -*- coding: utf-8 -*-

import pymysql
from VideoSpider import settings as config
from sqlalchemy import create_engine

pymysql.install_as_MySQLdb()


def get_engine(product=True, db="video"):
    if product:
        engine = create_engine(
            'mysql+mysqldb://{}:{}@{}:{}/{}'.format(
                config.MYSQL_USER,
                config.MYSQL_PASSWD,
                config.MYSQL_HOST,
                config.MYSQL_PORT,
                config.MYSQL_DB
            ),
            connect_args={'charset': 'utf8'}
        )
    else:
        engine = create_engine(
            'mysql+mysqldb://{}:{}@{}:{}/{}'.format(
                config.TEST_MYSQL_USER,
                config.TEST_MYSQL_PASSWD,
                config.TEST_MYSQL_HOST,
                config.TEST_MYSQL_PORT,
                config.TEST_MYSQL_DB
            ),
            connect_args={'charset': 'utf8'}
        )
    return engine
