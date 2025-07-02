# Melt With Me

A live-feed of me dying in my apartment from heat.  
https://watchmemelt.bisonopolis.de/  

Original source for reading the `CO2-Monitor AIRCO2NTROL MINI 31.5006` device: https://hackaday.io/project/5301/logs?sort=oldest  

## Note

I kept the python3 translation of the original code and some simple scripts here for reference for myself and anyone who would wants to build something with this and getting an easy and modifiable starting point.   

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

This may differ from system to system, but what worked for me (Ubuntu 24.04):  

* run `ll -l /dev/hidraw*`
  * look fot the highest number of hidraw, eg `/dev/hidraw22`  
    * if there is no `hidraw` device, it's fine too
* plugin the `CO2-Monitor AIRCO2NTROL MINI`
* run `ll -l /dev/hidraw*` again
* the now highest number of `hidraw` devices is the CO2-Monitor
* run `sudo chmod o+rw /dev/hidrawNIMBER` for your device (replace NUMBER with the number you observed before)

Note: `sudo chmod o+rw /dev/hidrawNIMBER` has to be run after every reboot, there are multiple ways to make it permanent, one is at the bottom of the original post https://hackaday.io/project/5301/logs?sort=oldest.  


### Config

You can just fill in the variable in the conf-files directly, but that would make updating hard, so it's recommended to male local configs as following:   

Client:  
Copy `conf.py` to `conf_local.py` and fill out the variables.  

Server:  
Copy `web/conf.php` to `web/conf_local.php` and fill out the variables.  

Copy the `web` folder to your server.    
It has to be reachable from a root-path, eg: https://watchmemelt.bisonopolis.de/  

Run `simpleMonitorPoster.py`.  
