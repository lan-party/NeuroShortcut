# NeuroShortcut
A brain-computer interface tool for triggering keyboard shortcuts, system commands, and macro scripts by changing mental states
![Screen Recording](assets/screenrecording.gif)
## Getting Started
#### Windows 10
[Executable Download](https://github.com/lan-party/NeuroShortcut/releases/download/v0.1.1/NeuroShortcut.zip)
#### From Source
```
pip install -r requirements.txt
```
```
python NeuroShortcut.py
```
## Supported Devices
This project was made using the 8 channel OpenBCI Cyton board for EEG data capture. Support for more devices and electrode configurations will be added in the future.
![Screenshot 1](assets/screenshot1.png)
## Frequency Band Thresholding
Triggers are built on modulating activity in different regions of the brain and in different frequency bands. [Learn more here](https://mentalhealthdaily.com/2014/04/15/5-types-of-brain-waves-frequencies-gamma-beta-alpha-theta-delta/)

Control methods based on motor imagery and sensory evoked potentials will be added at some point.
![Screenshot 2](assets/screenshot2.png)
## Actions
The current version of NeuroShortcut can execute system commands from mental triggers. Future versions will be able to activate keyboard shortcuts and replay mouse movements as well.
![Screenshot 3](assets/screenshot3.png)

Also check out [BCIWiki](https://bciwiki.org) to learn more about the possibilities with neurotech!
