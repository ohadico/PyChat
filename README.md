# PyChat

**protocol**
1. client connect to the server and send his name
    * '|' and spaces are not allowed
    * name must be unique
    * name cannot be empty string
2. In case of error, server send error message and disconnect,
   otherwise server send "SUCCESS".

Then client can send these commands to the server:
* "get clients"
  * server return list of clients names separated by '|'
    * the asking client is included in the list 
* "get messages"
  * server return list messages directed to the client separated by '|'
    * the messages are in the format "[from_client] [msg]" 
* "send to [name] [msg]"
  * send direct message to other client
  * client will get the message when it ask the server
