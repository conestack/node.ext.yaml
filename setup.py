from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test
import os


def read_file(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return f.read()


version = '0.2.dev0'
shortdesc = 'Node tree implementation for yaml files'
longdesc = '\n\n'.join([read_file(name) for name in [
    'README.rst',
    'CHANGES.rst',
    'LICENSE.rst'
]])


class Test(test):

    def run_tests(self):
        from node.ext.yaml import tests
        tests.run_tests()


setup(
    name='node.ext.yaml',
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='node yaml',
    author='Node Contributors',
    author_email='dev@conestack.org',
    url='https://github.com/conestack/node.ext.yaml',
    license='Simplified BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['node', 'node.ext'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'node',
        'plumber',
        'pyyaml',
        'setuptools'
    ],
    extras_require=dict(
        test=[
            'zope.testrunner'
        ]
    ),
    tests_require=[
        'zope.testrunner'
    ],
    cmdclass=dict(test=Test)
)
