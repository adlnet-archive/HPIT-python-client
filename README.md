# HPIT (Hyper-Personalized Intelligent Tutor) Python Client Libraries

## What is HPIT?

HPIT is a collection of machine learning and data management plugins for Intelligent Tutoring Systems. It
is being developed between a partnership with Carnegie Learning and TutorGen, Inc and is based on the most 
recent research available. The goal of HPIT is to provide a scalable platform for the future development 
of cognitive and intelligent tutoring systems. HPIT by default consists of several different plugins
which users can store, track and query for information. As of today we support Bayesian Knowledge Tracing, 
Models Tracing, Adaptive Hint Generation, and data storage and retrieval. HPIT is in active development 
and should be considered unstable for everyday use.

## Installing the client libraries

1. To install the client libraries make sure you are using the most recent version of Python 3.4.
    - On Ubuntu: `sudo apt-get install python3 python-virtualenv`
    - On Mac w/ Homebrew: `brew install python3 pyenv-virtualenv`

2. Setup a virtual environment: `virtualenv -p python3 env`
3. Active the virtual environment: `source env/bin/activate`
4. Install the HPIT client libraries: `pip3 install hpitclient`

You're all set to start using the libraries.

## Running the test suite.

1. Activate the virtual environment: `source env/bin/activate`
2. Install the testing requirements: `pip3 install -r test_requirements.txt`
3. Run the nose tests runner: `nosetests`

## Registering with HPIT

## Creating a Plugin

## Creating a Tutor