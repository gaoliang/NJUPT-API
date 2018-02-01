try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

with open("README.MD", encoding='utf-8') as f:
    long_description = f.read()

install_requires = open("requirements.txt").readlines()

setup(
    name='njupt',
    version='0.1',
    platforms='any',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    url='https://github.com/gaoliang/NJUPT-API',
    license='MIT License',
    author='gaoliang',
    install_requires=install_requires,
    author_email='gaoliangim@gmail.com',
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.dat'],
    },
    description='njupt api for humans',
    long_description=long_description,
)
