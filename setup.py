from setuptools import setup, find_packages

install_requires = ['TexSoup', 'nbformat']
tests_require = ['pytest']

setup(
    name='tex2ipy',
    version='0.1',
    author='Prabhu Ramachandran',
    author_email='prabhu@aero.iitb.ac.in',
    description='Convert beamer presentations to IPython notebooks',
    url='https://github.com/prabhuramachandran/tex2ipy',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    package_dir={'tex2ipy': 'tex2ipy'},
    entry_points="""
        [console_scripts]
        tex2ipy = tex2ipy.cli:main
    """
)
