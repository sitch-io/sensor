# Expecto Cabronum

We expect the following env vars to be set:

        LOG_HOST   # host:port
        LOG_METHOD  # local_file or direct.  Local file expects that the logstash-forwarder daemon is shipping logs.  direct sends right from the output thread, no file or logstash-forwarder daemon.  Not thoroughly tested.  No intelligent queue management in the event it's unable to reach the server.
        VAULT_URL # https://vault_host.com:port
        VAULT_LS_CERT_PATH # Path to logstash cert (secret/logstash-fwd-crt)
        VAULT_TOKEN # token for accessing cred
        KAL_GAIN # Gain setting for Kalibrate (try 80)
        KAL_BAND # Band to scan with Kalibrate (try GSM850)
        SIM808_BAND # Band to scan with SIM808 (try GSM850_MODE)
        SIM808_PORT # Device for tty (try /dev/ttyUSB0)
        MODE  # setting this to 'clutch' will cause it to loop before all the fun stuff starts.  Great for when you're troubleshooting in the Resin console.
        


Optionally:
        LOCATION_NAME  # Override the default device naming, which is Resin device ID
