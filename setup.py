import os
from setuptools import setup

README = """
See the README on `GitHub
<https://github.com/uw-it-aca/scheduled-job-client>`_.
"""

# The VERSION file is created by travis-ci, based on the tag name
version_path = 'scheduled_job_client/VERSION'
VERSION = open(os.path.join(os.path.dirname(__file__), version_path)).read()
VERSION = VERSION.replace("\n", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

url = "https://github.com/uw-it-aca/scheduled-job-client"
setup(
    name='scheduled-job-client',
    version=VERSION,
    packages=['scheduled_job_client'],
    author="UW-IT AXDD",
    author_email="aca-it@uw.edu",
    include_package_data=True,
    install_requires=[
        'Django>=1.10,<1.11',
        'django-aws-message>=1.0.1,<1.1',
        'boto3',
    ],
    license='Apache License, Version 2.0',
    description=('App to provide support for scheduled-job-manager'),
    long_description=README,
    url=url,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)
