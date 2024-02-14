![Logo](https://pub.files.multilan.de/ik-bus-tool/logo.png)

## I∕K-Bus Tool  
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
Requirements are included in the packaged version.
- PyQt6
- pyserial
- python3
- (pip3)
 
### Install

#### Windows
Download package for [Windows](https://pub.files.multilan.de/ik-bus-tool/1.0/win/I%E2%80%89%E2%88%95%E2%80%89K-Bus%20Tool.exe)

#### macOS
Download package for [Mac](https://pub.files.multilan.de/ik-bus-tool/1.0/mac/I%E2%80%89%E2%88%95%E2%80%89K-Bus%20Tool.app.zip)

#### Manual/Others
Clone the repo

```git clone https://git.multilan.de/tarek/ik-bus-tool.git```

Navigate to the project directory and install the requirements

```python3 -m pip install -r requirements.txt```

Run the python script main.py

```python3 main.py```

You may need to set the right permissions on the serial device, otherwise you may get a permission error.


### License
Distributed under the [GPLv3](https://pub.files.multilan.de/license.txt) license 