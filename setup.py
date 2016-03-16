from distutils.core import setup

setup(
    name = 'RpPlotter',
    version = '0.1.0',
    packages = ['rpplotter',],
    license = 'MIT',
    description = 'An application that simplifies generating Nyquist and polarization resistance plots from electrochemical impedance spectroscopy data.',
    long_description = open('README.md').read(),
    url = 'https://github.com/bocklund/rp-plotter',
    author = 'Brandon Bocklund',
    author_email = 'brandonbocklund@gmail.com',
    install_requires = ['numpy','matplotlib','pandas',],
)
