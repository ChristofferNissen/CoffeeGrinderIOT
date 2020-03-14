# How to (re)deploy with Vagrant

For some reason ``` vagrant up ``` is not working, so the vm will have to be created by hand from the web interface...

However, 
after getting the iot_rsa key from @niss which should be placed in ~/.ssh/ folder, run ``` vagrant provision ```

this will take the content of server, and rsync it to the remote vm, and reexecute the docker-compose script. That should be it :-)