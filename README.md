# Python CLI Chat

This is a simple client, server Python script that \
manages chat rooms. chatting is via CLI

## Tech stack
1. python's socket library - manage connections and conversations
2. python's threading library - for concurrency
3. My own SocketUtils module - a simple module that makes managing tcp client and servers easier


## How to install requirements
Go to the root of the project and run this command
```bash
pip install -r requirements.txt
```

## How to set up the server
When running the program you need to choose a port on which to bind the server to. you can do this by using the -p flag or the --port argument. Example:
```bash
python src/server/server.py -p 8080
```
Now, because the server program listens on localhost, you will need to forward the port using some kindd of a service.
This tutorial will use __Ngrok__, but you can choose whatever service you want.

### Setting up ngrok
1. Follow the instructions on https://dashboard.ngrok.com/get-started/ (from step 1 to the authtoken step )
2. run the command:
   ```bash
    ngrok tcp PORT
    ```
where PORT is the port of choice you put in server.py (remember that if you didn't specify any port when running the server, it will be 8080 by default).

You should see something like this:
![img.png](img.png)

copy the link that starts with __tcp://__.

When connecting to the server in client.py, \
the server address should be from the first character after the tcp:// until the ':'.
and the port will be the other part.

#### Example
__link:__ tcp://4.tcp.eu.ngrok.io:1234 \
__SERVER_ADDRESS:__ 4.tcp.eu.ngrok.io \
__PORT:__ 1234

Please make sure you set these variables in shared/entities.py like showed