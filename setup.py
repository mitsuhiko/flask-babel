"""
Flask-Babel
-----------

Adds i18n/l10n support to Flask applications with the help of the
`Babel`_ library.

Links
`````

* `documentation <http://packages.python.org/Flask-Babel>`_
.. _Babel: http://babel.edgewall.org/

"""
from setuptools import setup


setup(
    name='Flask-Babel',
    version='0.8',
    url='http://github.com/mitsuhiko/flask-babel',
    license='BSD',
    author='Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    description='Adds i18n/l10n support to Flask applications',
    long_description=__doc__,
    py_modules=['flask_shorturl'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'Babel',
        'pytz',
        'speaklater>=1.2',
        'Jinja2>=2.5'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
