Elotouch
========

I needed my old 17" touchscreen ELO ET1525L to work but I have not found any working touch driver especially for ARM board like Raspberry Pi.

The ET1525L has a serial interface with a very simple protocol already handled by 
Vojtech Pavlik's code here: http://lxr.free-electrons.com/source/drivers/input/touchscreen/elo.c
Although compiled into the kernel I was not able to finally load and use it on Raspberry Pi.

But that was needed in this manual: http://who-t.blogspot.fi/2012/07/elographics-touchscreen-setup.html
for loading touchscreen driver.

I have instead written a python script for emulating the Linux event device.
Up to now only 10 byte protocol is supported - 4 and 6 byte protocol could be easily implemented.

The python script uses python-uinput module 
https://github.com/tuomasjjrasanen/python-uinput

Before running the elotouch driver load the uinput like described at python-uinput:

```
modprobe uinput
```

or add it to /etc/modules

To have the touch device running on startup the script should be added to rc.local.

Once loaded you also can use xinput_calibrator to calibrate your touchscreen.
See build instructions for xinput_calibrator:
http://engineering-diy.blogspot.co.uk/2013/01/adding-7inch-display-with-touchscreen.html



Installation
------------

Open a commandline, go into this folder and enter

```
python setup.py install
```

Afterwards you can start the program with typing 

```
elotouch.py
```


Usage
-----

Simply run elotouch.py --help for a complete list of options.

It is possible to run the script also on Windows where no uinput can be installed. 
Then the script operates in sniff mode automatically. 
So you will be able to simply test your touch screen (do not forget to add some verbosity to see logs).



