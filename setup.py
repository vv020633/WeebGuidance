from distutils.core import setup

# import build_ui
try:
    from pyqt_distutils.build_ui import build_ui
    cmdclass = {'build_ui': build_ui}
except ImportError:
    build_ui = None  # user won't have pyqt_distutils when deploying
    cmdclass = {}

setup(
    name='WeebGuidance',
    version='1.0',
    author='Chas McLaughlin',
    author_email='weebguidance@gmail.com',
    packages=['weeb-Guidance',],
    install_requires=['PyQt5', 'python3-bs4'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
    cmdclass=cmdclass,
)