# Hatch Take Home Exercise
## Multi client In Memory Datastore Server
### Jean-Michel Bouchard

- Assumptions
    - Most important assumption, out of the multiple clients, none of them will start a transaction at the same time. While they're free to start a transaction, rollback a transaction or commit an existing transaction, implementing a multi client / multi transactional (but synchronized globally). I made sure that the KeyValueStore is an interface that can be re-implemented to make it easy to switch in or out.
    - Used a TCP socket server in order to guarantee transmission of data / de-duplication just to make our lives easier.
    - Currently the default max number of clients is 5 as implemented in the TCP Server class, but can be modified if necessary.
    - Added an "EXIT"/"exit" (basically any combination that can be lowercased to "exit") command to close the connection gracefully. Can always CTRL-C on a connection but it seemed out of scope to handle that gracefully without an exception on the server side.
    - Added some basic logs just to show that multiple clients connect on different ports.
    - Serving traffic on port 4000 by default.

- Code Structure
    - src -> source code of the program
        - api -> the API that sits in front of the datastore, in order to seperate the available functionality from implementation of the datastore
        - datastore -> implementation of the datastore itself
        - handler -> code for the client handler (how to read data from the socket stream) and the parser (how to parse commands)
        - model -> code for the response object
        - server -> code for the socket server
    - tests -> tests for the program

- Commands
    - Space is the delimiting character between commands and arguments. We split up to a maximum of 2 spaces which means in the context of <CMD> <KEY> <VALUE>, neither the command or the key can contain spaces but the value can contain spaces.
    - The handler for commands will only read 1024 UTF-8 characters which imply that the maximum size of a command (in the context of PUT specifically) will be 1024 - 3 (for PUT) - 2 (space between PUT and <key> and space between <key> and <value>) will be 1019 characters. Obviously, this assumes we only use UTF-8 characters that use one byte (so no copyright symbols, letters with accents, etc....). If this feature was required or we would want more bytes for a command (let's say we want to store much bigger sized blobs..) we would have to rethink our socket reading strategy. Thankfully, all of that is isolated in the client handler.

- Usage
    - Makefile has been made available to make the process easier.
        - `make venv` to make the virtual environment
        - `make tests` to run tests
        - `make run` to start the server
        - `nc 0.0.0.0 4000` to connect one client to the server. If you want multiple clients, just start more processes.

- Notes
    - Yes, ChatGPT was leveraged to write the tests (of course I validated), if a tool exists, why not use it to speed up the process... just smart engineering in my opinion.
    - Right now, it seems the kv_api is not super useful since it mostly just calls the datastore implementation. The reason is modularity, let's say we want to implement different strategies for transactions, it makes it easy to switch the implementation. Another use would be validation of inputs, let's say we only want to support key sizes of 20 bytes, we could validate it there. Same for logging. Let's say we want a different type of handler, HTTP or gRPC, we just need endpoints and a reference to the singleton, now we can expose the catch to other services without needing for them to implement socket clients directly. Actually scratch that, I had forgotten to edit the response so now kv_api seems a bit more useful and it was much more trivial to refactor!
