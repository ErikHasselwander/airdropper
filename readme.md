# Instructions

1. Download the latest version of python.
2. Clone this repo
3. Add your .csv file to the repo-folder.
    - It should have the format: Sending wallet,ASA ID,Amount,Recieveing wallet
    - It uses decimal dot in amount, and algo has ASA ID 0.
4. Optional: If you intend for the script to sign and send transactions you need to add your mnemonic to private.py
    - You will be prompted for confirmation twice, with time in between to review output .csv files with what the script intends to do.
    - It is only on row 3 that you input your mnemonic, nothing else needs changing!
        - Input as MNEMONIC = "word1 word2 word3 ... word24 word25"
4. Open CMD and navigate to the repo folder.
5. Install the only prerequisite py-algo-sdk by running the command `pip install py-algorand-sdk` (or `pip3 install py-algorand-sdk`) 
    - Should work to do `py -m pip install py-algorand-sdk` or `python3 -m pip install py-algorand-sdk` or the same with pip3 instead of pip. Depends on a lot of stuff but give all a try before you deem it impossible!
5. Run the script using `py sender.py` (or `python3 sender.py`)
6. Follow the prompts in your terminal.

# How do I interpret the output .csv files?
It is quite simple. missing_optin.csv will show all the transactions that were ignored due to missing optins. pending_transactions.csv show what transactions the bot instends to send, and also a header-row which contains what group they are inside of. Once the script is run final_output.csv will show what groups failed and what groups succeeded, and you then corroborate this against the pending_transactions.csv to see which tx's need to be manually sent.

This is so far untested for actually sending transactions. Please reach out to me on discord, Swaggelwander#7655, if there are any issues. Always test scripts before running them hot. Also big thanks to the WAGEROO team who incentivized this project with their first tech bounty!