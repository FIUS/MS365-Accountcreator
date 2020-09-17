"""
Setup
"""
from setuptools import setup

setup(
    name='ms365_accountcreator',
    packages=['ms365_accountcreator'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_sqlalchemy',
        'flask_jwt_extended',
        'flask_bcrypt',
        'flask_cors',
        'ldap3',
    ],
)
