from distutils.core import setup

requirements = [
    'requests (>=2.2.1)',
]

classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Environment :: MacOS X',
    'Environment :: Win32 (MS Windows)',
    'Environment :: X11 Applications',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'License :: OSI Approved :: MIT License',
    'License :: OSI Approved :: Python Software Foundation License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows :: Windows 7',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Topic :: Adaptive Technologies',
    'Topic :: Education :: Computer Aided Instruction (CAI)',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    'Topic :: Scientific/Engineering :: Human Machine Interfaces',
    ]

setup(name='hpitclient',
    version='0.26',
    description='Python Client Libraries for HPIT.',
    author='TutorGen, Inc.',
    author_email='rchandler@tutorgen.com',
    maintainer='Raymond Chandler III',
    maintainer_email='rchandler@tutorgen.com',
    url='https://github.com/tutorgen/HPIT-python-client',
    download_url='https://github.com/tutorgen/HPIT-python-client',
    platforms=['linux', 'mac osx', 'windows 7', 'windows 8'],
    license='MIT LICENSE',
    packages=['hpitclient'],
    classifiers=classifiers,
    requires=requirements,
)
