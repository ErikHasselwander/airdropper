# Instructions

1. Download the latest version of python.
 - Windows only: Make sure that "scripts are added to path"
2. Clone this repo
3. Add your .csv file to the repo-folder.
 - It should have the format: Sending wallet,ASA ID,Amount,Recieveing wallet
 - It uses decimal dot in amount, and algo has ASA ID 0.
4. Optional: If you intend for the script to sign and send transactions you need to add your mnemonic to private.py
 - You will be prompted for confirmation twice, with time in between to review output .csv files with what the script intends to do.
4. Open CMD and navigate to the repo folder.
5. Install the only prerequisite py-algo-sdk by running the command `pip install py-algorand-sdk` (or `pip3 install py-algorand-sdk`) 
5. Run the script using `py sender.py` (or `python3 sender.py`)
6. Follow the prompts in your terminal.