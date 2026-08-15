from django.conf import settings

def test_database_is_postgresql():
    assert settings.DATABASES["default"]["ENGINE"].endswith("postgresql")
