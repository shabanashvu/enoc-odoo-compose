=====================
MuK REST API for Odoo
=====================

Enables a REST API for the Odoo server. The API has routes to authenticate
and retrieve a token. Afterwards, a set of routes to interact with the server
are provided. The API can be used by any language or framework which can make
an HTTP requests and receive responses with JSON payloads and works with both
the Community and the Enterprise Edition.

The API allows authentication via OAuth1 and OAuth2 as well as with username
and password, although an access key can also be used instead of the password.
The documentation only allows OAuth2 besides basic authentication. The API has
OAuth2 support for all 4 grant types. More information about the OAuth 
authentication can be found under the following links:

* `OAuth1 - RFC5849 <https://tools.ietf.org/html/rfc5849>`_
* `OAuth2 - RFC6749 <https://tools.ietf.org/html/rfc6749>`_


Requirements
============

OAuthLib
-------------

A generic, spec-compliant, thorough implementation of the OAuth request-signinglogic
for Python. To install OAuthLib please follow the `instructions <https://pypi.org/project/oauthlib/>`_
or install the library via pip.

``pip install oauthlib``


Installation
============

To install this module, you need to:

Download the module and add it to your Odoo addons folder. Afterward, log on to
your Odoo server and go to the Apps menu. Trigger the debug mode and update the
list by clicking on the "Update Apps List" link. Now install the module by
clicking on the install button.

Another way to install this module is via the package management for Python
(`PyPI <https://pypi.org/project/pip/>`_).

To install our modules using the package manager make sure
`odoo-autodiscover <https://pypi.org/project/odoo-autodiscover/>`_ is installed
correctly. Note that for Odoo version 11.0 and later this is not necessary anymore. 
Then open a console and install the module by entering the following command:

``pip install --extra-index-url https://nexus.mukit.at/repository/odoo/simple <module>``

The module name consists of the Odoo version and the module name, where
underscores are replaced by a dash.

**Module:**

``odoo<version>-addon-<module_name>``

**Example:**

``sudo -H pip3 install --extra-index-url https://nexus.mukit.at/repository/odoo/simple odoo14-addon-muk-rest``

Once the installation has been successfully completed, the app is already in the
correct folder. Log on to your Odoo server and go to the Apps menu. Trigger the
debug mode and update the list by clicking on the "Update Apps List" link. Now
install the module by clicking on the install button.

The biggest advantage of this variant is that you can now also update the app
using the "pip" command. To do this, enter the following command in your console:

``pip install --upgrade --extra-index-url https://nexus.mukit.at/repository/odoo/simple <module>``

When the process is finished, restart your server and update the application in
Odoo. The steps are the same as for the installation only the button has changed
from "Install" to "Upgrade".

You can also view available Apps directly in our `repository <https://nexus.mukit.at/#browse/browse:odoo>`_
and find a more detailed installation guide on our `website <https://mukit.at/page/open-source>`_.

For modules licensed under a proprietary license, you will receive the access data after you purchased
the module. If the purchase were made at the Odoo store please contact our `support <support@mukit.at>`_
with a confirmation of the purchase to receive the corresponding access data.

Upgrade
============

To upgrade this module, you need to:

Download the module and add it to your Odoo addons folder. Restart the server
and log on to your Odoo server. Select the Apps menu and upgrade the module by
clicking on the upgrade button.

If you installed the module using the "pip" command, you can also update the
module in the same way. Just type the following command into the console:

``pip install --upgrade --extra-index-url https://nexus.mukit.at/repository/odoo/simple <module>``

When the process is finished, restart your server and update the application in
Odoo, just like you would normally.


Configuration
=============

In case the module should be active in every database just change the auto install flag to ``True``. 
To activate the routes even if no database is selected the module should be loaded right at the server 
start. This can be done by editing the configuration file or passing a load parameter to the start script.

Parameter: ``--load=web,muk_rest``

To access the api in a multi database enviroment without a db filter, the name of the database must be
provided with each request via the db parameter.

Parameter: ``?db=<database_name>``

To configure this module, you need to:

#. Go to *Settings -> API -> Dashboard*. Here you can see an overview of all your APIs.
#. Click on *Create* or go to either *Restful API -> OAuth1* or *Restful API -> OAuth2* to create a new API.

To extend the API and to add your own routes, go to *Settings -> API -> Endpoints* and create a new endpoint.
An endpoint can be both public and protected and is then only accessible via authentication. An endpoint can
either evaluate a domain, perform a server action or execute python code.

Its possible to further customize the API via a set of parameters insde the config file. The following table
shows the possible parameters and their corresponding default value.

+----------------------------+--------------------------------------------------------------------------+-----------------------------------+
| Parameter                  | Description                                                              | Default                           |
+----------------------------+--------------------------------------------------------------------------+-----------------------------------+
| rest_default_cors          | Sets the CORS attribute on all REST routes                               | None                              |
+----------------------------+--------------------------------------------------------------------------+-----------------------------------+
| rest_docs_security_group   | Reference an access group to protect the API docs for unauthorized users | None                              |
+----------------------------+--------------------------------------------------------------------------+-----------------------------------+
| rest_docs_codegen_url      | Service to generate REST clients                                         | https://generator3.swagger.io/api |
+----------------------------+--------------------------------------------------------------------------+-----------------------------------+
| rest_authentication_basic  | Defines if the Basic authentication is active on the REST API            | True                              |
+----------------------------+--------------------------------------------------------------------------+-----------------------------------+
| rest_authentication_oauth1 | Defines if the OAuth1 authentication is active on the REST API           | True                              |
+----------------------------+--------------------------------------------------------------------------+-----------------------------------+
| rest_authentication_oauth2 | Defines if the OAUth2 authentication is active on the REST API           | True                              |
+----------------------------+--------------------------------------------------------------------------+-----------------------------------+

Parameters from an configuration file can be loaded via the ``--config`` command.


Usage
=====

You are able to use the API with a client of your choice or use the client generator as a starting point. 
For documentation go to *Settings -> API -> Documentation -> Endpoints*


Credit
======

Contributors
------------

* Mathias Markl <mathias.markl@mukit.at>

Images
------

Some pictures are based on or inspired by:

* `Font Awesome <https://fontawesome.com>`_
* `Prosymbols <https://www.flaticon.com/authors/prosymbols>`_
* `Smashicons <https://www.flaticon.com/authors/smashicons>`_

Author & Maintainer
-------------------

This module is maintained by the `MuK IT GmbH <https://www.mukit.at/>`_.

MuK IT is an Austrian company specialized in customizing and extending Odoo.
We develop custom solutions for your individual needs to help you focus on
your strength and expertise to grow your business.

If you want to get in touch please contact us via `mail <sale@mukit.at>`_
or visit our `website  <https://mukit.at>`_.
