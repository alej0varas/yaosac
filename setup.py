from setuptools import setup
import os


README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()


setup(
    name="yaosac",
    version=__import__('yaosac').__version__,
    author="Alexandre Varas",
    author_email="alej0varas@gmail.com",
    py_modules=['yaosac', ],
    include_package_data=True,
    install_requires=['requests', ],
    license='GNU Library or Lesser General Public License (LGPL)',
    description="Yet another OneSignal API Client",
    long_description=README,
    url='https://github.com/alej0varas/yaosac',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='onesignal push notification client api sdk',
    test_suite="tests",
)
