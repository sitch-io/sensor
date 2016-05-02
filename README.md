# Expecto Cabronum

We expect the following env vars to be set:

        LOG_HOST   # host:port
        VAULT_URL # https://vault_host.com:port
        VAULT_LS_CERT_PATH # Path to logstash cert (secret/logstash-fwd-crt)
        VAULT_TOKEN # token for accessing cred
        KAL_GAIN # Gain setting for Kalibrate (try 80)
        KAL_BAND # Band to scan with Kalibrate (try GSM850)
        SIM808_BAND # Band to scan with SIM808 (try GSM850_MODE)
        SIM808_PORT # Device for tty (try /dev/ttyUSB0)


Optionally:
        LOCATION_NAME  # Override the default device naming, which is Resin device ID
