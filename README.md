# ZK ADMS

This python script is acts as a middle man between the zkTeco biometrics & RBS server

## Prerequisite
python version 3.xx up

## First Setup
```bash
# setups a virtual environment. this is optional as we can install the dependency on the pi itself.
python -m venv venv
source venv/bin/activate

# installing the dependencies
pip isntall -r requirements.txt

# see if it runs:
python app.py
```

## Registering the script on Systemd

choose editor of choice(vi, vim, nano)
edit the properties on zkADMS.service:
  - Description(optional)
  - ExecStart(required)
  - WorkingDirectory(required)
  - User(required)


```bash
# copy the systemService file to the /etc/systemd/system
sudo cp ./zkADMS.service /etc/systemd/system/zkADMS.service

# add an execute permission to the script:
sudo chmod +x /etc/systemd/system/zkADMS.service

# enable and start the service
sudo systemctl enable zkADMS.service
sudo systemctl start zkADMS.service

# check the status:
sudo systemctl status zkADMS.service 
```
