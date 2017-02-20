from setuptools import setup, find_packages


def get_readme_rst():
    import subprocess
    try:
        proc = subprocess.Popen(
            ['pandoc', 'README.md', '--to', 'rst'],
            stdout=subprocess.PIPE
        )
        description = proc.communicate()[0].decode()
    except OSError:
        with open('README.md') as fp:
            description = fp.read()
    return description


def get_version():
    import os
    data = {}
    fname = os.path.join('tex2ipy', '__init__.py')
    exec(compile(open(fname).read(), fname, 'exec'), data)
    return data.get('__version__')


install_requires = ['TexSoup', 'nbformat']
tests_require = ['pytest']


classes = """
Development Status :: 3 - Alpha
Environment :: Console
Framework :: IPython
Intended Audience :: Developers
Intended Audience :: Education
Intended Audience :: End Users/Desktop
Intended Audience :: Science/Research
License :: OSI Approved :: BSD License
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3 :: Only
Topic :: Software Development :: Libraries
Topic :: Utilities
"""

classifiers = [x.strip() for x in classes.splitlines() if x]

setup(
    name='tex2ipy',
    version=get_version(),
    author='Prabhu Ramachandran',
    author_email='prabhu@aero.iitb.ac.in',
    description='Convert beamer presentations to IPython notebooks',
    long_description=get_readme_rst(),
    license="BSD",
    url='https://github.com/prabhuramachandran/tex2ipy',
    classifiers=classifiers,
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    package_dir={'tex2ipy': 'tex2ipy'},
    entry_points="""
        [console_scripts]
        tex2ipy = tex2ipy.cli:main
    """
)
