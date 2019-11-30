from pathlib import Path
from setuptools import find_packages, setup
from typing import List, Union

import pipfile
import re
import subprocess


def read_file(path: Union[str, Path]) -> str:
    with Path(path).open('r') as f:
        return f.read().strip()


def infer_version() -> str:
    process = subprocess.run(['git', 'describe'], stdout=subprocess.PIPE)
    output = process.stdout.decode('utf-8').strip()
    version = re.sub('^v', '', output)
    return version


def load_requirements() -> List[str]:
    # return read_file('requirements.txt').splitlines()
    return [f'{package}{version}' for package, version in pipfile.load().data['default'].items()]


def read_python_version() -> str:
    return pipfile.load().data['_meta']['requires']['python_version']


setup(name='aws-sso',
      version=infer_version(),
      url='https://github.com/rkhullar/aws-sso',
      author='Rajan Khullar',
      author_email='rkhullar03@gmail.com',
      long_description=read_file('readme.md'),
      long_description_content_type='text/markdown',
      keywords='aws sso',
      license='MIT',
      packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
      python_requires='~='+read_python_version(),
      install_requires=load_requirements(),
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose', 'parameterized'],
      entry_points={'console_scripts': ['aws-sso=aws_sso.command_line:main']}
      )
