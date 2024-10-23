Installing Redis From Source
As my great-great-grandfather said, nothing builds grit like installing from source. This section will walk you through downloading, making, and installing Redis. I promise that this won’t hurt one bit!

Note: This section is oriented towards installation on Mac OS X or Linux. If you’re using Windows, there is a Microsoft fork of Redis that can be installed as a Windows Service. Suffice it to say that Redis as a program lives most comfortably on a Linux box and that setup and use on Windows may be finicky.

First, download the Redis source code as a tarball:

$ redisurl="http://download.redis.io/redis-stable.tar.gz"
$ curl -s -o redis-stable.tar.gz $redisurl
Next, switch over to root and extract the archive’s source code to /usr/local/lib/:

$ sudo su root
$ mkdir -p /usr/local/lib/
$ chmod a+w /usr/local/lib/
$ tar -C /usr/local/lib/ -xzf redis-stable.tar.gz
Optionally, you can now remove the archive itself:

$ rm redis-stable.tar.gz
This will leave you with a source code repository at /usr/local/lib/redis-stable/. Redis is written in C, so you’ll need to compile, link, and install with the make utility:

$ cd /usr/local/lib/redis-stable/
$ make && make install
Using make install does two actions:

The first make command compiles and links the source code.

The make install part takes the binaries and copies them to /usr/local/bin/ so that you can run them from anywhere (assuming that /usr/local/bin/ is in PATH).

Here are all the steps so far:

$ redisurl="http://download.redis.io/redis-stable.tar.gz"
$ curl -s -o redis-stable.tar.gz $redisurl
$ sudo su root
$ mkdir -p /usr/local/lib/
$ chmod a+w /usr/local/lib/
$ tar -C /usr/local/lib/ -xzf redis-stable.tar.gz
$ rm redis-stable.tar.gz
$ cd /usr/local/lib/redis-stable/
$ make && make install
At this point, take a moment to confirm that Redis is in your PATH and check its version:

$ redis-cli --version
redis-cli 5.0.3
If your shell can’t find redis-cli, check to make sure that /usr/local/bin/ is on your PATH environment variable, and add it if not.

In addition to redis-cli, make install actually leads to a handful of different executable files (and one symlink) being placed at /usr/local/bin/:

$ # A snapshot of executables that come bundled with Redis
$ ls -hFG /usr/local/bin/redis-* | sort
/usr/local/bin/redis-benchmark*
/usr/local/bin/redis-check-aof*
/usr/local/bin/redis-check-rdb*
/usr/local/bin/redis-cli*
/usr/local/bin/redis-sentinel@
/usr/local/bin/redis-server*
While all of these have some intended use, the two you’ll probably care about most are redis-cli and redis-server, which we’ll outline shortly. But before we get to that, setting up some baseline configuration is in order.


Remove ads
Configuring Redis
Redis is highly configurable. While it runs fine out of the box, let’s take a minute to set some bare-bones configuration options that relate to database persistence and basic security:

$ sudo su root
$ mkdir -p /etc/redis/
$ touch /etc/redis/6379.conf
Now, write the following to /etc/redis/6379.conf. We’ll cover what most of these mean gradually throughout the tutorial:

# /etc/redis/6379.conf

port              6379
daemonize         yes
save              60 1
bind              127.0.0.1
tcp-keepalive     300
dbfilename        dump.rdb
dir               ./
rdbcompression    yes
Redis configuration is self-documenting, with the sample redis.conf file located in the Redis source for your reading pleasure. If you’re using Redis in a production system, it pays to block out all distractions and take the time to read this sample file in full to familiarize yourself with the ins and outs of Redis and fine-tune your setup.

Some tutorials, including parts of Redis’ documentation, may also suggest running the Shell script install_server.sh located in redis/utils/install_server.sh. You’re by all means welcome to run this as a more comprehensive alternative to the above, but take note of a few finer points about install_server.sh:

It will not work on Mac OS X—only Debian and Ubuntu Linux.
It will inject a fuller set of configuration options into /etc/redis/6379.conf.
It will write a System V init script to /etc/init.d/redis_6379 that will let you do sudo service redis_6379 start.
The Redis quickstart guide also contains a section on a more proper Redis setup, but the configuration options above should be totally sufficient for this tutorial and getting started.

Security Note: A few years back, the author of Redis pointed out security vulnerabilities in earlier versions of Redis if no configuration was set. Redis 3.2 (the current version 5.0.3 as of March 2019) made steps to prevent this intrusion, setting the protected-mode option to yes by default.

We explicitly set bind 127.0.0.1 to let Redis listen for connections only from the localhost interface, although you would need to expand this whitelist in a real production server. The point of protected-mode is as a safeguard that will mimic this bind-to-localhost behavior if you don’t otherwise specify anything under the bind option.

With that squared away, we can now dig into using Redis itself.

Ten or So Minutes to Redis
This section will provide you with just enough knowledge of Redis to be dangerous, outlining its design and basic usage.

Getting Started
Redis has a client-server architecture and uses a request-response model. This means that you (the client) connect to a Redis server through TCP connection, on port 6379 by default. You request some action (like some form of reading, writing, getting, setting, or updating), and the server serves you back a response.

There can be many clients talking to the same server, which is really what Redis or any client-server application is all about. Each client does a (typically blocking) read on a socket waiting for the server response.

The cli in redis-cli stands for command line interface, and the server in redis-server is for, well, running a server. In the same way that you would run python at the command line, you can run redis-cli to jump into an interactive REPL (Read Eval Print Loop) where you can run client commands directly from the shell.

First, however, you’ll need to launch redis-server so that you have a running Redis server to talk to. A common way to do this in development is to start a server at localhost (IPv4 address 127.0.0.1), which is the default unless you tell Redis otherwise. You can also pass redis-server the name of your configuration file, which is akin to specifying all of its key-value pairs as command-line arguments:

$ redis-server /etc/redis/6379.conf
31829:C 07 Mar 2019 08:45:04.030 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
31829:C 07 Mar 2019 08:45:04.030 # Redis version=5.0.3, bits=64, commit=00000000, modified=0, pid=31829, just started
31829:C 07 Mar 2019 08:45:04.030 # Configuration loaded
We set the daemonize configuration option to yes, so the server runs in the background. (Otherwise, use --daemonize yes as an option to redis-server.)

Now you’re ready to launch the Redis REPL. Enter redis-cli on your command line. You’ll see the server’s host:port pair followed by a > prompt:

127.0.0.1:6379>
Here’s one of the simplest Redis commands, PING, which just tests connectivity to the server and returns "PONG" if things are okay:

127.0.0.1:6379> PING
PONG
Redis commands are case-insensitive, although their Python counterparts are most definitely not.

Note: As another sanity check, you can search for the process ID of the Redis server with pgrep:

$ pgrep redis-server
26983
To kill the server, use pkill redis-server from the command line. On Mac OS X, you can also use redis-cli shutdown.

Next, we’ll use some of the common Redis commands and compare them to what they would look like in pure Python.


Remove ads
Redis as a Python Dictionary
Redis stands for Remote Dictionary Service.

“You mean, like a Python dictionary?” you may ask.

Yes. Broadly speaking, there are many parallels you can draw between a Python dictionary (or generic hash table) and what Redis is and does:

A Redis database holds key:value pairs and supports commands such as GET, SET, and DEL, as well as several hundred additional commands.

Redis keys are always strings.

Redis values may be a number of different data types. We’ll cover some of the more essential value data types in this tutorial: string, list, hashes, and sets. Some advanced types include geospatial items and the new stream type.

Many Redis commands operate in constant O(1) time, just like retrieving a value from a Python dict or any hash table.

Redis creator Salvatore Sanfilippo would probably not love the comparison of a Redis database to a plain-vanilla Python dict. He calls the project a “data structure server” (rather than a key-value store, such as memcached) because, to its credit, Redis supports storing additional types of key:value data types besides string:string. But for our purposes here, it’s a useful comparison if you’re familiar with Python’s dictionary object.

Let’s jump in and learn by example. Our first toy database (with ID 0) will be a mapping of country:capital city, where we use SET to set key-value pairs:

127.0.0.1:6379> SET Bahamas Nassau
OK
127.0.0.1:6379> SET Croatia Zagreb
OK
127.0.0.1:6379> GET Croatia
"Zagreb"
127.0.0.1:6379> GET Japan
(nil)
The corresponding sequence of statements in pure Python would look like this:

>>> capitals = {}
>>> capitals["Bahamas"] = "Nassau"
>>> capitals["Croatia"] = "Zagreb"
>>> capitals.get("Croatia")
'Zagreb'
>>> capitals.get("Japan")  # None
We use capitals.get("Japan") rather than capitals["Japan"] because Redis will return nil rather than an error when a key is not found, which is analogous to Python’s None.

Redis also allows you to set and get multiple key-value pairs in one command, MSET and MGET, respectively:

127.0.0.1:6379> MSET Lebanon Beirut Norway Oslo France Paris
OK
127.0.0.1:6379> MGET Lebanon Norway Bahamas
1) "Beirut"
2) "Oslo"
3) "Nassau"
The closest thing in Python is with dict.update():

>>> capitals.update({
...     "Lebanon": "Beirut",
...     "Norway": "Oslo",
...     "France": "Paris",
... })
>>> [capitals.get(k) for k in ("Lebanon", "Norway", "Bahamas")]
['Beirut', 'Oslo', 'Nassau']
We use .get() rather than .__getitem__() to mimic Redis’ behavior of returning a null-like value when no key is found.

As a third example, the EXISTS command does what it sounds like, which is to check if a key exists:

127.0.0.1:6379> EXISTS Norway
(integer) 1
127.0.0.1:6379> EXISTS Sweden
(integer) 0
Python has the in keyword to test the same thing, which routes to dict.__contains__(key):

>>> "Norway" in capitals
True
>>> "Sweden" in capitals
False
These few examples are meant to show, using native Python, what’s happening at a high level with a few common Redis commands. There’s no client-server component here to the Python examples, and redis-py has not yet entered the picture. This is only meant to show Redis functionality by example.

Here’s a summary of the few Redis commands you’ve seen and their functional Python equivalents:






The Python Redis client library, redis-py, that you’ll dive into shortly in this article, does things differently. It encapsulates an actual TCP connection to a Redis server and sends raw commands, as bytes serialized using the REdis Serialization Protocol (RESP), to the server. It then takes the raw reply and parses it back into a Python object such as bytes, int, or even datetime.datetime.

Note: So far, you’ve been talking to the Redis server through the interactive redis-cli REPL. You can also issue commands directly, in the same way that you would pass the name of a script to the python executable, such as python myscript.py.

So far, you’ve seen a few of Redis’ fundamental data types, which is a mapping of string:string. While this key-value pair is common in most key-value stores, Redis offers a number of other possible value types, which you’ll see next.
