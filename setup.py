import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

README = read('README.rst')

setup(
    name = "django-agenda",
    version = "20100618",
    url = 'http://github.com/glibersat/django-agenda',
    license = 'GPL v3',
    description = "A generic implementation of a web-based calendar with events.",
    long_description = README,

    author = 'Mathijs de Bruin',
    author_email = 'mathijs@visualspace.nl',
    packages = [
        'agenda',
    ],
    package_data = {
    },
    requires = [
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPL License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
