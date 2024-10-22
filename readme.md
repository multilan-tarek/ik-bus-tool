![Logo](https://pub.files.multilan.de/ik-bus-tool/logo.png)

## I/K-Bus Tool  
LIN-Bus (BMW I/K-Bus Protocol) Logger & Writer  

![Screenshot](https://pub.files.multilan.de/ik-bus-tool/screenshot.png)
  
### Features  
- Logging  
- Saving to binary file  
- Saving to text file with hex formatted content  
- Saving to readable formatted text file  
- Writing data using the UI  
- Writing data from files with configurable interval  
- Tool to convert text to data  
  
### Requirements
Requirements are included in the packaged versions.
- PyQt6
- pyserial
- python3
- (pip3)
 
### Install

#### Windows
Download [Package](https://pub.files.multilan.de/ik-bus-tool/1.0/win/I%E2%80%89%E2%88%95%E2%80%89K-Bus%20Tool.exe) for Windows

Download [Setup](https://pub.files.multilan.de/ik-bus-tool/1.0/win/I%20%E2%88%95%20K-Bus%20Tool%20Setup.exe) for Windows 

#### macOS
Download [Package](https://pub.files.multilan.de/ik-bus-tool/1.0/mac/I%E2%80%89%E2%88%95%E2%80%89K-Bus%20Tool.zip) for macOS

#### Manual/Others
Clone the repo

```git clone https://git.multilan.de/tarek/ik-bus-tool.git```

Navigate to the project directory and create a virtual environment

```python3 -m pip venv .venv```

Install the requirements

```.venv/bin/pip3 -m pip install -r requirements.txt```

Run the python script main.py

```.venv/bin/python3 main.py```

You may need to set the right permissions on the serial device, otherwise you may get a permission error.


### License
Distributed under the [GPLv3](https://pub.files.multilan.de/license.txt) license 