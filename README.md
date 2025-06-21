#  SshGui :  a python/gtk utility to manage ssh config files

it manage : 
- ssh keys, public and private
- authorized_keys file , with possible ssh options
- ssh config file, including sub-config included files
- known-hosts file

it manage the current user .ssh directory or any remote-user@remote-machine , if you have the right to do so
( you public key must be installed manually in the remote user authorized_keys )


