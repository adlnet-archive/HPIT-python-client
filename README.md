# HPIT (Hyper-Personalized Intelligent Tutor) Python Client Libraries

## What is HPIT?

HPIT is a collection of machine learning and data management plugins for Intelligent Tutoring Systems. It
is being developed between a partnership with Carnegie Learning and TutorGen, Inc and is based on the most 
recent research available. The goal of HPIT is to provide a scalable platform for the future development 
of cognitive and intelligent tutoring systems. HPIT by default consists of several different plugins
which users can store, track and query for information. As of today we support Bayesian Knowledge Tracing, 
Model Tracing, Adaptive Hint Generation, and data storage and retrieval. HPIT is in active development 
and should be considered unstable for everyday use.

## Installing the client libraries

1. To install the client libraries make sure you are using the most recent version of Python 3.4.
    - On Ubuntu: `sudo apt-get install python3 python-virtualenv`
    - On Mac w/ Homebrew: `brew install python3 pyenv-virtualenv`

2. Setup a virtual environment: `virtualenv -p python3 env`
3. Active the virtual environment: `source env/bin/activate`
4. Install the HPIT client libraries:
    1. First, clone the repository at https://github.com/tutorgen/HPIT-python-client.git.
    2. Run 'python setup.py install'

You're all set to start using the libraries.

## Running the test suite.

1. Activate the virtual environment: `source env/bin/activate`
2. Install the testing requirements: `pip3 install -r test_requirements.txt`
3. Run the nose tests runner: `nosetests`

## Registering with HPIT

Go to https://www.hpit-project.org/user/register and create a new account.

## Settings

There are various settings which change the behavior of the client side libraries.

| name               | default                        | description                                |
|--------------------|--------------------------------|--------------------------------------------|
| HPIT_URL_ROOT      | 'https://www.hpit-project.org' | The URL of the HPIT server.                |
| REQUESTS_LOG_LEVEL | 'debug'                        | The logging level of the requests library. |

To override the clientside settings in your app do the following. You will need to override the HPIT
URL if you are doing any local testing.

```python
    from hpitclient.settings import HpitClientSettings
    settings = HpitClientSettings.settings()
    settings.HPIT_URL_ROOT = 'http://127.0.0.1:8000'
```

## Plugins

### Tutorial: Creating a Plugin

To create a new plugin, first go https://www.hpit-project.org and log in. Then
click on "My Plugins" and add a new plugin. Give it a brief name and a description. Click
Submit. The next page will generate for you two items you'll need to us to connect to the
centralized HPIT router. An Entity ID and an API Key. We do not store API Keys on the server
so if you lose it you'll need to generate a new one. Copy the Entity ID and API Key.

To create a new plugin you'll need to derive from the Plugin class.

```python
from hpitclient import Plugin

class MyPlugin(Plugin):

    def __init__(self):
        entity_id = 'YOUR_PLUGIN_ENTITY_ID' #eg. b417e82d-4153-4f87-8a11-8bb5c6bfaa00
        api_key = 'YOUR_PLUGIN_API_KEY' #eg. ae29bd1b81a6064061eca875a8ff0a8d

        #Call the parent class's init function
        super().__init__(entity_id, api_key)
```

Calling the start method on the plugin will connect it to the server.

```python

my_plugin = MyPlugin()
my_plugin.start()
```

Plugins are event driven. The start method connects to the server then starts an endless loop. There are
several hooks that can get called in this process. One of these hooks is the `post_connect` hook and will
get called after successfully connecting to the server. Here is where you can register the messages you want
your plugin to listen to and the callback functions to call when your plugin recieves a message of that type.

Let's define one now:

```python
from hpitclient import Plugin

class MyPlugin(Plugin):

    def __init__(self):
        ...

    def post_connect(self):
        super().post_connect()

        #Subscribe to a message called 'echo'
        self.subscribe(echo=self.my_echo_callback)

    def my_echo_callback(self, message):
        print(message['echo_text'])
```

The `self.subscribe` method takes a message name and a callable. In this case `echo` is the message name and
`self.my_echo_callback` is the callback that will be called when a message of that name is sent to the plugin. It 
then contacts the HPIT central router and tells it to start storing messages with that name of `echo` so this plugin
can listen to and respond to those messages.

A message in HPIT consists of a message name, in this case `echo` and a payload. The payload can
have any arbitrary data in it that a tutor wishes to send. HPIT doesn't care about the kind of data
it sends to plugins. It's the plugin operator's responsibility to do what it wants with the data
that comes from the tutor.

So now if a tutor sends a message like `"echo" -> {'echo_text' : "Hello World!"}` through HPIT this plugin
will recieve that message and print it to the screen. If 'echo_text' isn't in the payload the callback would
throw a KeyError exception so we might want to handle that.

```python

from hpitclient import Plugin

class MyPlugin(Plugin):

    def __init__(self):
        ...

    def post_connect(self):
        ...

    def my_echo_callback(self, message):
        if 'echo_text' in message:
            print(message['echo_text'])
```

In the inner loop of the start method a few things happen. The plugin asks the HPIT router server if any messages
that it wants to listen to are queued to be sent to the plugin. Then if it recieves new messages it dispatches them
to the assigned callbacks that were specified in your calls to `self.subscribe`

Plugins can also send responses back to the original sender of messages. To do so the plugin needs to call the
`self.send_response` function. All payloads come with the `message_id` specified so we can route responses appropriately.
To send a response we'll need to slightly modify our code a bit.

```python

from hpitclient import Plugin

class MyPlugin(Plugin):

    def __init__(self):
        ...

    def post_connect(self):
        ...

    def my_echo_callback(self, message):
        if 'echo_text' in message:
            #Print the echo message
            print(message['echo_text'])

            #Send a response to the message sender 
            my_response = {
                'echo_response': message['echo_text']
            }
            self.send_response(message['message_id'], my_response)
```

Now the original tutor or plugin who sent this message to your MyPlugin will get a response back
with the `echo_response` parameter sent back.

Just like tutors, plugins can also send messages to other messages over HPIT. It is possible to
"daisy chain" plugins together this way where you have a tutor send a message, which gets sent 
to a plugin (A), which queries another plugin for information (B), which does the same for another plugin (C), 
which sends back a response to plugin B, which responds to plugin A, which responds to the original Tutor.

The goal with this is that each plugin can handle a very small task, like storing information, do some logging,
update a decision tree, or a knowledge graph, or etc, etc. The possibilities are endless.

Our plugin all put together now looks like:

```python
from hpitclient import Plugin

class MyPlugin(Plugin):

    def __init__(self):
        entity_id = 'YOUR_PLUGIN_ENTITY_ID' #eg. b417e82d-4153-4f87-8a11-8bb5c6bfaa00
        api_key = 'YOUR_PLUGIN_API_KEY' #eg. ae29bd1b81a6064061eca875a8ff0a8d

        #Call the parent class's init function
        super().__init__(entity_id, api_key)

    def post_connect(self):
        super().post_connect()

        #Subscribe to a message called 'echo'
        self.subscribe(echo=self.my_echo_callback)

    def my_echo_callback(self, message):
        if 'echo_text' in message:
            #Print the echo message
            print(message['echo_text'])

            #Send a response to the message sender 
            my_response = {
                'echo_response': message['echo_text']
            }
            self.send_response(message['message_id'], my_response)


if __name__ == '__main__':
    my_plugin = MyPlugin()
    my_plugin.start()
```

### Plugin Hooks

There are several hooks throughout the main event loop, where you can handle some special cases. The only hook
that MUST be defined in a plugin is the `post_connect` hook. It is where you should define the messages and handlers
that the plugin to listen and possibly respond to. 

To stop the plugin from running you can either send a SIGTERM or SIGKILL signal to it eg. (`sudo kill -9 plugin_process_id`), OR
you can press CTRL+C, OR you can return False from a hook. A signal, control+c, and returning False from a hook are considered
graceful by the library and not only will the plugin terminate, it will send a disconnect message to the server, which will
destory the authentication session against the server, and the HPIT server will continue storing messages for you to retrieve
later.

Disconnecting from the HPIT server will not cause HPIT to forget about you, it will continue storing messages for you, which
you can recieve the next time you run your plugin. Isn't that nice. :)

If you want HPIT to stop storing and routing messages to you, you can call the handy, dandy 'self.unsubscribe' method after
connecting to HPIT. A good place to do this is in the `pre_disconnect` hook.

```python
from hpitclient import Plugin

class MyPlugin(Plugin):

    def __init__(self):
        pass

    def post_connect(self):
        super().post_connect()

        #Subscribe to a message called 'echo'
        self.subscribe(echo=self.my_echo_callback)

    def pre_disconnect(self):
        #Unsubscribe to the 'echo' message
        self.unsubscribe('echo')
```

Here are some other places you can hook into the event loop. Returning False from any of them, will cause the event loop to
terminate.

Hook Name                   | Called When:
--------------------------- | --------------------------------------------------------------------------
pre_connect                 | Before the plugin connects and authenticates with the server.
post_connect                | After the plugin connects and authenticates with the server.
pre_disconnect              | Before the plugin disconnects from the server.
post_disconnect             | After the plugin disconnects from the server. (Right before exit)
pre_poll_messages           | Before the plugin polls the server for new messages.
post_poll_messages          | After the plugin polls the server for new messages but before dispatch.
pre_dispatch_messages       | Before the messages are dispatched to their callbacks.
post_dispatch_messages      | After the messages are dispatched to their callbacks.
pre_handle_transactions     | Before the plugin polls the server for new PSLC Datashop transactions.
post_handle_transcations    | After the plugin polls the server for new PSLC Datashop transactions.
pre_poll_responses          | Before the plugin polls the server for new responses to it's messages.
post_poll_responses         | After the plugin polls the server for new responses but before dispatch.
pre_dispatch_responses      | Before the plugin dispatches it's responses to response callbacks.
post_dispatch_responses     | After the plugin dispatches it's responses to response callbacks.


## Tutors

### Tutorial: Creating a Tutor

To create a new tutor, first go https://www.hpit-project.org and log in. Then
click on "My Tutors" and add a new tutor. Give it a brief name and a description. Click
Submit. The next page will generate for you two items you'll need to us to connect to the
centralized HPIT router. An Entity ID and an API Key. We do not store API Keys on the server
so if you lose it you'll need to generate a new one. Copy the Entity ID and API Key.

To create a new tutor you'll need to derive from the Tutor class.

```python
from hpitclient import Tutor

class MyTutor(Tutor):

    def __init__(self):
        entity_id = 'YOUR_PLUGIN_ENTITY_ID' #eg. b417e82d-4153-4f87-8a11-8bb5c6bfaa00
        api_key = 'YOUR_PLUGIN_API_KEY' #eg. ae29bd1b81a6064061eca875a8ff0a8d

        super().__init__(entity_id, api_key, self.main_callback)

    def main_callback(self):
        print("Main Callback Loop")
        response = self.send('echo', {'test': 1234})
```

Tutors differ from plugins in one major way, in their main event loop they call a callback function
which will be called during each iteration of the main event loop. This callback is specified in a 
parameter in the init function. After calling the main callback function, the main event loop then
polls HPIT for responses from plugins which you have sent messages to earlier.

To send a message to HPIT and have that message routed to a specific plugin you can call the `self.send`
method as we do above. Messages sent this way consist of an event name (in this case 'echo') and a dictionary
of data. Optionally you can specify a response callback as we do below. All messages sent through HPIT are 
multicast and every plugin which 'subscribes' to those messages will recieve them, including the echo plugin
you created and registered with HPIT in the last tutorial.

```python
class MyTutor(Tutor):
    ...

    def main_callback(self):
        response = self.send('echo', {'test': 1234}, self.response_callback)

    def response_callback(self, response):
        print(str(response))
```

When you send a message to HPIT you can specify a response callback to the send method. After the message is
recieved and processed by a plugin, it may optionally send a response back. If it does the response will travel
back through HPIT, where when polled by this library, will route that response to the callback you specified. You can
then process the response however you would like in your Tutor. Here, we are just echoing the response back to the
console. Responses you recive will be a dictionary consisting of the following key-value pairs.

Key (. denotes sub-dictionary)  | Value
------------------------------- | --------------------------------------------------------------------------
message_id                      | The ID generated to track the message.
message.sender_entity_id        | Your Entity ID.
message.receiver_entity_id      | The Plugin's Entity ID that is responding to your message.
message.time_created            | The time HPIT first recieved your message.
message.time_received           | The time HPIT queued the message for the plugin to consume.
message.time_responded          | The time HPIT recieved a response from the plugin.
message.time_response_received  | The time HPIT sent the response back to your tutor.
message.payload                 | What you originally sent to HPIT.
message.message_name            | What you named the message.
response                        | A dictionary of values the Plugin responded to the message with.

Since multiply plugins may respond to the same message that you sent out, you may wish to check the contents
of the response payload, as well as the message.reciever_entity_id to help filter the responses you actually
want to handle. You can specify different callbacks for the same message, as well as a "global" callback for 
one message. For example both:

```python
class mytutor(tutor):
    ...

    def main_callback(self):
        response = self.send('echo', {'test': 1234}, self.response_callback)
        response = self.send('echo_two', {'test': 1234}, self.response_callback)

    def response_callback(self, response):
        print(str(response))
```

AND

```python
class mytutor(tutor):
    ...

    def main_callback(self):
        response = self.send('echo', {'test': 1234}, self.response_callback)
        response = self.send('echo', {'test': 1234}, self.response_callback_two)

    def response_callback(self, response):
        print(str(response))

    def response_callback_two(self, response):
        logger.log(str(response))
```

are valid ways to handle responses from plugins. 

That's really all their is to writing a tutor.


## A Note about Transactions

In HPIT, a transaction is supposed to be the smallest unit of interaction a student has with a tutor.  The
PSLC datashop uses transactions in its analysis of learning; it is the most fine grained representation of a
student's skill set.  Transactions can be generated by the student, like a key being press or an answer selected, 
or by the tutor, as in the tutor tells HPIT that the student was correct in answering a question.

For a Tutor, to utilize transactions, developers should make use of the send_transaction() method, which functions
similarly to the send() method, except it issues a special "transaction" message to HPIT.

For a Plugin, they must specifically set a transaction callback using register_transaction_callback(), which also
subscribes a tutor to transaction messages.


## Active Plugins in Production

Currently, there are only 2 plugins active on HPIT's production servers which you can query for information.
These are the knowledge tracing plugin and the hint factory plugin. The knowledge tracing plugin is responsible
for handling bayesian knowledge tracing, and the hint factory handle domain model generation and hint generation.
Documentation on these two plugins are available from https://www.hpit-project.org/docs