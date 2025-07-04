# Melt With Me

A live-feed of me dying in my apartment from heat.  
https://watchmemelt.bisonopolis.de/  

Original source for reading the `CO2-Monitor AIRCO2NTROL MINI 31.5006` device: https://hackaday.io/project/5301/logs?sort=oldest  

## Note

I kept the python3 translation of the original code and some simple scripts here for reference for myself and anyone who would wants to build something with this and getting an easy and modifiable starting point.   

### Device Infos

`usb-devices | grep -B4 -A4 USB-zyTemp`
```
P:  Vendor=04d9 ProdID=a052 Rev=01.00
S:  Manufacturer=Holtek
S:  Product=USB-zyTemp
```

`udevadm info --query=property --name=/dev/hidraw4`  
``` 
DEVPATH=/devices/pci0000:00/0000:00:08.1/0000:c5:00.3/usb1/1-2/1-2.1/1-2.1:1.0/>
DEVNAME=/dev/hidraw4
MAJOR=241
MINOR=4
SUBSYSTEM=hidraw
USEC_INITIALIZED=1733790499
ID_VENDOR_FROM_DATABASE=Holtek Semiconductor, Inc.
ID_MODEL_FROM_DATABASE=USB-zyTemp
```

## Requirements

* Any Linux computer with python3
* A webserver with PHP
* A URL / subdomain

The `CO2-Monitor AIRCO2NTROL MINI 31.5006 | TFA Dostmann`
* https://www.tfa-dostmann.de/produkt/co2-monitor-airco2ntrol-mini-31-5006/
* Amazon Affiliate Link: https://amzn.to/44zvPGj
  * As an Amazon Associate I earn from qualifying purchases. 

## Setup

### CO2-Monitor

**Note:** Not setting the `DEVICE_PATH` in `conf_local.py` will result in auto-detecting the device path, which still needs the `rw` (read/write) rights to be set, but it will show you the path if it can be detected, making the manual guesswork superfluous.   

This may differ from system to system, but what worked for me (Ubuntu 24.04):  

* run `ll -l /dev/hidraw*`
  * look fot the highest number of hidraw, eg `/dev/hidraw22`  
    * if there is no `hidraw` device, it's fine too
* plugin the `CO2-Monitor AIRCO2NTROL MINI`
* run `ll -l /dev/hidraw*` again
* the now highest number of `hidraw` devices is the CO2-Monitor
* run `sudo chmod o+rw /dev/hidrawNUMBER` for your device (replace NUMBER with the number you observed before)

**Note:** `sudo chmod o+rw /dev/hidrawNUMBER` has to be run after every reboot, there are multiple ways to make it permanent, one is at the bottom of the original post https://hackaday.io/project/5301/logs?sort=oldest.  


### Config

You can just fill in the variable in the conf-files directly, but that would make updating hard, so it's recommended to male local configs as following:   

Client:  
Copy `conf.py` to `conf_local.py` and fill out the variables.  

Server:  
Copy `web/conf.php` to `web/conf_local.php` and fill out the variables.  

Copy the `web` folder to your server.    
It has to be reachable from a root-path, eg: https://watchmemelt.bisonopolis.de/  

Run `monitorPoster.py`.  
