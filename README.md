# Oratorio
A web-based speech coach that helps users improve their public speaking skills
through analysis of pacing, tone, and machine learning.

Project progress, including our SRS and SDS documents, can be tracked from [our Github pages](https://potatotank.github.io/oratorio/).

## How to build Oratorio

Currently only the UW CSE Linux home VM (CentOS) is supported.

This project uses Python 2.7 (pre-installed in the home VM) and Django 1.10.

To install Django:

~~~
sudo yum install python-pip
sudo pip install django==1.10
~~~

To install IBM Watson:
~~~
sudo pip install --upgrade watson-developer-cloud
~~~

To install oauth2:
~~~
sudo pip install oauth2client
~~~

To install Django Nose (For coverage testing):
~~~
sudo pip install django-nose coverage
~~~

### Installation

Download the latest release version of Oratorio from [our list of releases](https://github.com/PotatoTank/oratorio/releases). Or, clone this repository to obtain the latest development version of Oratorio.

### Setup

Firstly, set up your `secret_settings.py`:

- Go to `oratorio/coach/` and locate file named `secret_settings.py.template`
- Create a copy of it named `secret_settings.py`
- Fill in the fields in the template

Each field in secret_settings.py is explained in the following table:

| Field                              | Explanation                                                                                                                 |
|------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| `SECRET_KEY`                       | Django uses this key for cryptographic signing. To test locally, set to any unique, unpredictable value.                    |
| `ALLOWED_HOSTS`                    | Used to create a list of IP addresses / domains where this code can be hosted. This field is optional when testing locally. |
| `SPEECH_TO_TEXT_USER_NAME`         | Username for IBM Watson Speech-to-Text App.                                                                                 |
| `SPEECH_TO_TEXT_PASSWORD`          | Password for IBM Watson Speech-to-Text App.                                                                                 |
| `TONE_ANALYZER_USER_NAME`          | Username for IBM Watson Speech-to-Tone Analyzer App.                                                                        |
| `TONE_ANALYZER_PASSWORD`           | Password for IBM Watson Speech-to-Tone Analyzer App.                                                                        |
| `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` | Key used for Google login. Contact us for credentials.                                                                      |
| `EMOTION_API_KEY`                  | Key used for Beyond Verbal analysis. API                                                                                     |

Then, set up your database with:

~~~
python manage.py makemigrations coach
python manage.py migrate coach
~~~

### Usage

You can run a development server on localhost on port 8000 with:

`python manage.py runserver`

You can also run the test suite and get a coverage report with:

```
coverage run --source=coach.models,coach.analyzer,coach.views ./manage.py test
coverage report
```

Client side tests and coverage can be accessed while the django server is running at
[localhost:8000/static/client-tests.html](http://localhost:8000/static/client-tests.html?coverage).

### Directory structure

~~~
oratorio/ - Project directory
  manage.py - Django’s admin utility file
  coach/ - Main application directory
    tests/ - Tests for main application
    settings.py - Settings for the main application
    models.py - Contains models used to store data
    views.py - Contains instructions on how to handle web request
    urls.py - Contains mappings from url to page
    secret_settings.py.template - File used to contain secret credentials not committed to github
  templates/ - HTML templates for the whole project
    coach/
      devdocs.html - HTML code for the developer docs
      index.html - HTML code for the landing page with record button
      profile.html
      results.html - HTML code to display transcript and analysis
  static/ - Images, css and other static files for the whole project
    scripts.js - Contains javascript for record button
    sidebar.js - Contains javascript for sidebar menu button
    styles.css - Describes how different elements should be displayed
    wordFrequency.js - Contains javascript for highlighting most frequently used word

~~~

### Continuous integration setup

Set up Travis CI by following [this](https://travis-ci.org/getting_started) starter's guide. We set up Travis to run our test suite every time a commit is pushed, and to notify team members via email and Slack when a test fails.

### Adding a new release version

To release a new version, package the code in a tar file and create a new release through Github’s Releases feature. Detailed instructions can be found [here](https://help.github.com/articles/creating-releases/).

### Bug tracking

All bugs and issues should be reported to the [issue tracker](https://github.com/PotatoTank/oratorio/issues). Please follow the issue
template and be as informative as possible.

### Design Patterns
Here are two patterns that our team used:

**Model, View, Controller Pattern**: This pattern is used for user interfaces. It divides the software into three parts--the model, the view, and the controller--which separate the processes in which information is taken, processed, and shown to the user.

_Model_ --- Most of our backend is the model that analyzes the data and manipulates what to show to the user. One of these models is views.py which takes various informations such as transcript and statistics and sets them to display for the user.
_View_ --- The HTML pages located in oratorio/templates/coach/ as this is what is actually displayed to our user.
_Controller_ --- The controller is our website interface. The user can interact with the record button which sends data to the model to transcribe and analyze.


**Null Object Pattern**: This pattern is used to convey the absence of an object by using an object that doesn't do anything. An example of this would be the empty list.


We use this pattern when we use IBM Watson to get the transcript of an audio in `oratorio/coach/analyzer.py`. If the person does not say anything, instead of passing `None`, we pass an empty list as the transcript. This prevents any exceptions from being thrown.

### Style guideline enforcement

Set up pre-commit-hooks by editting `.pre-commit-config.yaml` following [this](https://github.com/pre-commit/pre-commit-hooks).
To use it, run the following lines in your root directory:
~~~
pip install pre-commit
pre-commit install
~~~
To skip the pep8 checker when committing:
~~~
SKIP=autopep8-wrapper git commit -m "foo"
~~~
To skip trailing whitespaces checker when committing:
~~~
SKIP=trailing-whitespace git commit -m "foo"
~~~
