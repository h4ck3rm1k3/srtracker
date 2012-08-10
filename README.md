Service Request Tracker
=======================

This web application is built for the City of Chicago as an interface to service requests submitted through their 311 system. It uses Chicago's Open311 API---including Chicago-specific extensions---to provide listings, lookups and subscription capabilities.

It includes the following components:
 - A web application for listing service requests, searching for a specific service request based on ID, and subscribing to email updates for specific service requests
 - A python script (in `/updater`) that checks the Open311 endpoint for 

![Screenshot of SR Tracker](https://raw.github.com/codeforamerica/srtracker/master/screenshot.png)

Installation & Configuration
----------------------------

You need to install an open311 compliant API server first, it is by default expected to be run on port 5000.
see http://open311.org for more details.

SRTracker's `app.py` web app requires the following python modules :

- flask
  debian package : python-flask - micro web framework based on Werkzeug, Jinja2 and good intentions

- requests 
  debian package : python-requests - elegant and simple HTTP library for Python, built for human beings

- iso8601
  no debian package,
  http://pypi.python.org/pypi/iso8601/
  pip-2.6 install iso8601

- dateutil 
  debian package : python-dateutil - powerful extensions to the standard datetime module

- psycopg2
  debian package : python-psycopg2 - Python-Modul for PostgreSQL

- configuration
 copy the file updater/configuration.py.example to updater/configuration.py and edit.

see also requirements.txt for detailed packages and version numbers.


SRTracker's `app.py` web app requires the following environment variables:

- `OPEN311_SERVER`: the fully qualified URL for the endpoint server, e.g. _'http://311.baltimorecity.gov/open311/v2'_
- `OPEN311_API_KEY`: the API key, [if necessary](http://wiki.open311.org/GeoReport_v2/Servers), for the Open311 server
- `PASSWORD_PROTECTED`: Whether SRTracker requires a password to access; for example, if it accesses a private/internal Open311 API
- `PASSWORD`: the password necessary to access this SRTracker instance

SRTracker's `updater.py` email update script requires email, database and other environment variables as defined in [`configuration_environ.py`](https://github.com/codeforamerica/srtracker/blob/master/updater/configuration_environ.py).

Chicago-specific Open311 Extensions
-----------------------------------

This application relies upon extensions to the [Open311 GeoReport v2 Spec](http://wiki.open311.org/GeoReport_v2) that are specific to Chicago (for the time being). These include:

- `updated_at` parameter: allows sorting requests by when they were updated, not just initially requests
- `notes` field: individual requests may have additional "follow-on" requests that define additional work/activities related to the initial request which are exposed in the `notes` field of an individual service request

## Contributing
In the spirit of [free software][free-sw], **everyone** is encouraged to help
improve this project.

[free-sw]: http://www.fsf.org/licensing/essays/free-sw.html

Here are some ways *you* can contribute:

* by using alpha, beta, and prerelease versions
* by reporting bugs
* by suggesting new features
* by translating to a new language
* by writing or editing documentation
* by writing specifications
* by writing code (**no patch is too small**: fix typos, add comments, clean up
  inconsistent whitespace)
* by refactoring code
* by closing [issues][]
* by reviewing patches
* [financially][]

[issues]: https://github.com/codeforamerica/straymapper/issues
[financially]: https://secure.codeforamerica.org/page/contribute

## Submitting an Issue

We use the [GitHub issue tracker][issues] to track bugs and features. Before submitting a bug report or feature request, check to make sure it hasn't already been submitted. You can indicate support for an existing issue by voting it up. When submitting a bug report, please include a [Gist][] that includes a stack trace and any details that may be necessary to reproduce the bug, including your gem version, Ruby version, and operating system. Ideally, a bug report should include a pull request with failing specs.

[gist]: https://gist.github.com/

## Submitting a Pull Request
1. Fork the project.
2. Create a topic branch.
3. Implement your feature or bug fix.
6. Commit and push your changes.
7. Submit a pull request.

## Copyright
Copyright (c) 2012 Code for America. See [LICENSE][] for details.

[license]: https://github.com/codeforamerica/cfa_template/blob/master/LICENSE.mkd