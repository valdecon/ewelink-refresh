"""Constants for the eWeLink Refresh integration."""

DOMAIN = "ewelink_refresh"

# Configuration
CONF_REGION = "region"
CONF_AUTO_DISCOVER = "auto_discover"
CONF_DEVICES = "devices"

# Defaults
DEFAULT_SCAN_INTERVAL = 60
DEFAULT_REGION = "eu"

# Regions
REGIONS = ["eu", "us", "cn", "as"]

# API URLs
API_URLS = {
    "us": "https://us-api.coolkit.cc:8080",
    "eu": "https://eu-api.coolkit.cc:8080",
    "cn": "https://cn-api.coolkit.cc:8080",
    "as": "https://as-api.coolkit.cc:8080",
}

# eWeLink App credentials
APP_ID = "oeVkj2lYFGnJu5XUtWisfW4utiN4u9Mq"
APP_SECRET = "6Nz4n0xA8s8qdxQf2GqurZj2Fs55FUvM"

# Power meter UIIDs
POWER_METER_UIDS = [
    '1', '2', '3', '4', '5', '6', '7', '8', '9',
    '15',   # POWR2
    '32',   # POW R3
    '44',   # POWR3
    '77',   # POWR316
    '81',   # POWR320D
    '82',   # POWR316D
    '126',  # POWR Elite
    '130',  # POWCT
    '133',  # MINIR4
    '136',  # DUALR3
    '138',  # S-MATE
    '151',  # ZBMINI-L2
    '154',  # THR316D
    '155',  # THR320D
    '173',  # MINIR3-1
    '174',  # MINIR3-2
    '175',  # S40
    '177',  # S40TPFB
    '181',  # NSPanel Pro
    '182',  # POWR3POW
]
