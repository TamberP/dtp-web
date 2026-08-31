# DTP-web

This is an offshoot of
[dtp-base](https://github.com/TamberP/dtp-base), but reworked and
refactored to provide a web interface, mostly so that I can use it on
my phone from work.

## What is it?

Much like DTP-base, it's a tool for digging through the UK Department
for Transport's roller brake-test database, in order to find brake
test procedures by DTP number, and other information. With 'advanced'
search functions to allow you to look up a DTP number from known
information about the vehicle/trailer, in cases where the VTG6 is not
present.

The database is pre-populated with the November 2020 DTP update
(V2101), described thusly:

> The attached files are for updating the vehicle database of ATF RBT's,
> The DVSA have requested that all units are updated by 1st
> November 2021. The update includes new Dtp numbers 9867 to 9958. (9958
> relates to a 3 axle Mercedes Benz rigid 26000kg GVW, Solo parking on
> axle 2&3, with the split service brake as the nominated secondary.)
> Therefore the existence of these additional numbers on your RBT data
> base will confirm if an update has been installed. this file format is
> for VLT units.

# Dependencies

Currently:
- Flask (3.1.3-ish)

and its dependencies:
- blinker (1.9.0)
- click   (8.4.2)
- itsdangerous (2.2.0)
- Jinja2  (3.1.6)
- MarkupSafe (3.0.3)
- Werkzeug (3.1.8)

# Running
## 'local' mode
*  `flask -A dtpweb run` from the project root
* point your web-browser to http://127.0.0.1:5000

## 'remote' mode

You will have to set up a WSGI server that serves up the flask app
returned by `dtpweb.create_app()`, which is an exercise left for the
reader.

Largely because I couldn't get it to work on my setup, so I just
bodged it with the `dtpweb.py` script that stands up a
`wsgiref.simple_server` on http://127.0.0.1:8000, and then
reverse-proxied it with my web-server. Do something similar if you
wish.

## Security

This doesn't handle any sensitive or personal data, it's just doing
lookups out of a local sqlite DB. There's a risk of sql injection that
in and of itself could only damage the lookup database, but I can't
guarantee that it *couldn't* be used to attack other things in the
system.

# Licensing
## The Database
The contents of the V2101/DTA database are a product of the Department
for Transport, and are public sector information licensed under the
Open Government License V3.0.

They are provided 'as-is', with no warranty, and the Department for
Transport are not liable for any errors or omissions.

For full terms, see:
https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/

The .sql files under V2101/ are created by myself as a simple
transformation of the contents of the .dta files, under the terms of
the OGL v3.0.

The DTA-base.sqlite database is produced mechanically from these
files, and is also licensed under the OGL v3.0

## The Code

[Except where otherwise noted, code is provided under the terms of the AGPL v3.0 license, a copy
of which is provided](LICENSE.md)

### _SQL_UTIL.PY
`_sql_util.py` is Copyright 2018 lemon24, provided by the
 [reader project](https://github.com/lemon24/reader), licensed under
 the BSD 3-clause license as below:
 Copyright 2018 lemon24

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1.  Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

2.  Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.

3.  Neither the name of the copyright holder nor the names of its
    contributors may be used to endorse or promote products derived from
    this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
