# count.re

![](https://badge.imagelayers.io/matthewgall/count.re:latest.svg) [![Docker Repository on Quay](https://quay.io/repository/matthewgall/count.re/status "Docker Repository on Quay")](https://quay.io/repository/matthewgall/count.re)

Sometimes we just need a counter, nothing magic, just a simple counter. Increment using a simple API, a click of a button or even via an e-mail. If you need this, then [count.re](https://count.re) is for you!

## Introducing count.re
Powered by Python and bottle, count.re is quick and simple to deploy, using all the power of [Docker](https://docker.io) you can be up and running in one command!

## Developing
To make editing easy, we're using Cloud9, an online IDE to allow you to get started quickly and simply! Getting started is easy, [click here](https://ide.c9.io/matthewgall/countre) and follow the instructions

## Deploying
Deploying count.re is easy using Docker:

    docker run -p 80:5000 matthewgall/count.re

Or via my quay.io mirror:

    docker run -p 80:5000 quay.io/matthewgall/count.re

Honestly, that simple (and none of that one line wget direct to your terminal)

## Features

### /version
Returns the current running version of count.re from the released commit hash

    $ curl https://count.re/version
    a54fda84993b524288b9597131f8d3aec3945e06


## Licence

    The MIT License (MIT)

    Copyright (c) 2015 Matthew Gall

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
