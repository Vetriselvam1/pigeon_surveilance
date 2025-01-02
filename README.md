Run Ngrok and Surveillance Script on Raspberry Pi
This guide provides instructions on how to set up a script that runs ngrok and surveillance.py in separate terminal windows on a Raspberry Pi.

Table of Contents
Overview
Prerequisites
Setup Instructions
Step 1: Create the Bash Script
Step 2: Make the Script Executable
Step 3: Run the Script
Step 4: Troubleshooting
Step 5: Optional – Add Script to Startup
Conclusion
Overview
This project provides a script that:

Runs the surveillance.py Python script in the background.
Runs ngrok on port 5000 in a separate terminal window to expose the service publicly.
By using this method, both processes can run simultaneously in separate windows while keeping the terminal output visible for each process.

Prerequisites
Before proceeding with the setup, make sure you have the following installed:

Raspberry Pi with Raspbian or similar Linux distribution.
Python 3 installed and configured.
ngrok installed and set up.
lxterminal installed (this is typically the default terminal on Raspberry Pi).
Setup Instructions
Step 1: Create the Bash Script
Open your terminal on the Raspberry Pi.

Navigate to the home directory or any directory where you want to save your script (e.g., /home/rbm/):

bash
Copy code
cd ~
Create a new file named run_ngrok.sh:

bash
Copy code
sudo nano /home/rbm/run_ngrok.sh
Paste the following code into the script:

bash
Copy code
#!/bin/bash
# Wait for the desktop environment to load
sleep 9

# Set the display environment for GUI applications
export DISPLAY=:0
export XAUTHORITY=/home/rbm/.Xauthority

# Open a new terminal for the surveillance.py script
lxterminal -e "bash -c 'python3 /home/rbm/Downloads/ClickStore-main/surveillance.py; bash'" &

# Open a new terminal for ngrok
lxterminal -e "bash -c 'ngrok http 5000; bash'" &
Save the file and exit the editor:

Press Ctrl + O to save.
Press Enter to confirm.
Press Ctrl + X to exit.
Step 2: Make the Script Executable
Make the script executable by changing its file permissions:
bash
Copy code
sudo chmod +x /home/rbm/run_ngrok.sh
Step 3: Run the Script
Execute the script to run surveillance.py and ngrok in separate terminal windows:

bash
Copy code
/home/rbm/run_ngrok.sh
What happens when you run the script:

A new terminal window opens running the surveillance.py script.
Another terminal window opens running ngrok on port 5000.
Both terminals will remain open and show the output of the respective processes.
Step 4: Troubleshooting
Ensure lxterminal is installed: If you get an error saying lxterminal is not found, install it using:

bash
Copy code
sudo apt-get install lxterminal
Verify Python Installation: Check if Python 3 is properly installed:

bash
Copy code
python3 --version
Ensure ngrok is installed: If ngrok is not installed, download and install it from the official website. After downloading, use the following commands to install it:

bash
Copy code
sudo unzip ngrok-stable-linux-arm.zip
sudo mv ngrok /usr/local/bin
Check for any errors: If the script doesn't work as expected, check the terminal output for any error messages related to missing dependencies, wrong paths, or other issues.

Step 5: Optional – Add Script to Startup
If you want to automatically run the script every time your Raspberry Pi starts up, follow these steps:

Open the crontab configuration for the current user:

bash
Copy code
crontab -e
Add the following line at the end to run the script at startup:

bash
Copy code
@reboot /home/rbm/run_ngrok.sh
Save and exit the crontab editor.

Conclusion
By following these steps, you’ve successfully set up a script to run surveillance.py and ngrok in separate terminal windows on your Raspberry Pi. You can now run both processes simultaneously with ease, and you can also set up the script to run automatically on boot.

If you have any issues or need further assistance, feel free to reach out!
