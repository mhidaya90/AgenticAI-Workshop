Step 1: In your VDI, export all installed libraries

Open Terminal (inside VDI):

`pip freeze > requirements.txt` 

This creates a file: requirements.txt
→ It contains every library + version currently installed on your VDI.
Upload this file to GitHub or copy it to your local machine.


Step 2: On your local machine → create a virtual environment

`python3 -m venv .venv`
`source .venv/bin/activate`   # Mac

Step 3: Install all VDI libraries in one command

Inside the activated venv:

`pip install -r requirements.txt`
