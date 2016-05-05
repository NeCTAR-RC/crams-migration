
from rcportal_migration.settings import *

INSTALLED_APPS += (
    'django_nose',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'rcportal_migration.sqlite3'),
    }
}


TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--with-coverage',
    '--verbosity=2',
    '--cover-xml',  # produle XML coverage info
    '--cover-xml-file=coverage.xml',  # the coverage info file
    '--cover-package=crams/tests',
    '--cover-inclusive',
]
