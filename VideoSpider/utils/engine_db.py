# -*- coding: utf-8 -*-

import pymysql
from VideoSpider import settings as config
from sqlalchemy import create_engine

pymysql.install_as_MySQLdb()


def get_engine(product=True, db="videosite_test"):
    if product:
        engine = create_engine(
            'mysql+mysqldb://{}:{}@{}:{}/{}'.format(
                config.MYSQL_USER,
                config.MYSQL_PASSWD,
                config.MYSQL_HOST,
                config.MYSQL_PORT,
                db
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
                db
            ),
            connect_args={'charset': 'utf8'}
        )
    return engine

# mysql engine
mysql_engine = get_engine(product=True, db="videosite_test")
