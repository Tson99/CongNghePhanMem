class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "B\xb2?.\xdf\x9f\xa7m\xf8\x8a%,\xf7\xc4\xfa\x91"

    DB_NAME = "production-db"
    DB_USERNAME = "root"
    DB_PASSWORD = "Dotuansondnno1"

    IMAGE_UPLOADS = "F:/BKDN/CongNghePhanMem/app/static/img/uploads"

    SESSION_COOKIE_SECURE = True


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    # SERVER_NAME = "127.0.0.1:90"
    DB_NAME = "development-db"
    DB_USERNAME = "admin"
    DB_PASSWORD = "Dotuansondnno1"

    IMAGE_UPLOADS = "F:/BKDN/CongNghePhanMem/app/static/img/uploads"

    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    TESTING = True

    DB_NAME = "development-db"
    DB_USERNAME = "admin"
    DB_PASSWORD = "Dotuansondnno1"

    SESSION_COOKIE_SECURE = False