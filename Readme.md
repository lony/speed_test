Speed Test
=====

Tool retrieves performance metrics testing against preset offside servers. The tool also gatherers devices in the local network which could interfere with your test results. Last but not least the metrics are send to a predefined Google Sheet.

# Feature

* Use [speedtest-cli](https://github.com/sivel/speedtest-cli) to test against [servers around the world](http://www.speedtest.net)
    * Ping
    * Upload
    * Download
* Use [nmap](https://nmap.org/) to detected other systems in your network
* Upload data to a [Google Sheet](https://www.google.com/sheets/about/)
    * Authenticate using service account

# Run

* Clone repository
* Create a [Google Cloud service account](https://console.cloud.google.com/apis/credentials) and copy credentials as JSON
* Google Spreadsheet
    * Setup sheet inside your account
    * Use service account `client_email` to share sheet (found in credential JSON)
    * Create one tab for each server testing against
* Configuration in `speed_test_conf.json`
    * Set credential path
    * Copy sheet id
    * Configure network mask
    * Use [Speedtest homepage](http://www.speedtest.net) to gather server ids and enter them along with a sheet tab name as `location`
* Install packages needed `sudo apt-get install python3-pip nmap`
* Optional use `virtualenv` and run
    * `virtualenv -p /usr/local/bin/python3 venv --no-site-packages`
    * `source venv/bin/activate`
* Install python packages `pip install -r requirements.txt`
* `./speed_test.py`

# Automate (on Raspberry)

* Append the following lines to `/boot/config.txt` to disable wifi and Bluetooth

    ```
    # ---- Config
    dtoverlay=pi3-disable-wifi
    dtoverlay=pi3-disable-bt
    ```

* Run `crontab -e` and add the following entry to execute every hour

    ```
    PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games
    0 * * * *  /opt/speed_test/speed_test.py 2>&1 | /usr/bin/logger -t speed_test
    ```
