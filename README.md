# Python CLI Chat

This is a simple client, server Python script that \
manages chat rooms. chatting is via CLI

## Tech stack
1. python's socket library - manage connections and conversations
2. python's threading library - for concurrency
3. My own SocketUtils module - a simple module that makes managing tcp client and servers easier

## How to use the client app
First, go to [this link](https://github.com/eyalzwigen/python-cli-chat/releases/tag/client_app) and install the app (according to your OS)


## How to install requirements
Go to the root of the project and run this command
```bash
pip install -r requirements.txt
```

## How to set up the server
First go to server.py, and change SERVER_PORT to your port of choice.

Then go to your terminal. cd to the src folder.
then run the command: 
```bash
python server.py
```

then you need to forward the port. You can use any service of your choice.

This walkthrough will use ngrok.

### Setting up ngrok
1. Follow the instructions on https://dashboard.ngrok.com/get-started/ (from step 1 to the authtoken step )
2. run the command:
   ```bash
    ngrok tcp PORT
    ```
   where PORT is the port of choice you put in server.py.

You should see something like this:
![img.png](img.png)

copy the link that starts with __tcp://__.

When connecting to the server in client.py, \
the server address should be from the first character after the tcp:// until the ':'.
and the port will be the other part.

#### Example
__link:__ tcp://4.tcp.eu.ngrok.io:1234 \
__server address:__ 4.tcp.eu.ngrok.io \
__server port:__ 1234
