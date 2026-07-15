Setup and Operation
===================

Virtual environment
-------------------

Create and activate a Windows virtual environment:

.. code-block:: console

   py -3 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   python manage.py migrate
   python manage.py test
   python manage.py runserver

Docker
------

Build and run the application:

.. code-block:: console

   docker build -t news-capstone .
   docker run --rm -p 8000:8000 --env-file .env news-capstone

Secrets
-------

Copy ``.env.example`` to ``.env`` and provide private values locally.
Never commit passwords, secret keys, access tokens, private keys, databases,
or virtual-environment folders.
