---------------------------------------------
Understanding the Log Data Collected by Sitch
---------------------------------------------

The following sections describe the data for the files found in '/data/sitch/log/'.

.. include:: log_cells.rst

.. include:: log_geoip.rst

.. include:: log_gps.rst

.. include:: log_gsm_modem_channel.rst

.. include:: log_health_check.rst

.. include:: log_heartbeat.rst

.. include:: log_kal_channel.rst


sitch_alert.log
---------------

::

{"details": "Primary BTS was 310:260:275:20082 now 310:260:275:42302. Site: sitch-site-testing",
 "type": "Primary BTS metadata change.",
 "id": 110,
 "device_id": "sitch-site-testing"}


sitch_init.log
--------------

::

{"evt_data": "+COPS: 0\r\n",
 "evt_type": "registration",
 "evt_cls": "gsm_consumer"}

{"evt_data": "\r\n | OK\r\n | ATV1Q0&V \r\r\n | DEFAULT PROFILE\r\n | S0: 0\r\n | S3: 13\r\n | S4: 10\r\n | S5: 8\r\n | S6: 2\r\n | S7: 60\r\n | S8: 2\r\n | S10: 15\r\n | +CRLP: 61,61,48,6\r\n | V: 1\r\n | E: 1\r\n | Q: 0\r\n | X: 4\r\n | &C: 1\r\n | &D: 1\r\n | +CLTS: 0\r\n| +CREG: 0\r\n | +CGREG: 0\r\n | +CMEE: 0\r\n | +CIURC: 1\r\n | +CFGRI: 2\r\n | +CMTE: 0\r\n | +CANT: 0,0,10\r\n | +STKPCIS: 0\r\n | +CMGF: 0\r\n | +CNMI: 2,1,0,0,0\r\n | +CSCS: \"IRA\"\r\n | +VTD: 1\r\n | +CALS: 1\r\n | +CHF: 0\r\n | +CAAS: 1\r\n | +CBUZZERRING: 0\r\n | +DDET: 0\r\n | +MORING: 0\r\n | +SVR: 16\r\n | +CCPD: 1\r\n | +CSNS: 0\r\n | +CSGS: 1\r\n | +CNETLIGHT: 1\r\n | +SLEDS: 64,64,64,800,3000,300\r\n | +CSDT: 0\r\n | +CSMINS: 0\r\n | +EXUNSOL: 0\r\n | +FSHEX: 0\r\n | +FSEXT: 0\r\n | +IPR: 0\r\n | +IFC: 0,0\r\n | +CSCLK: 0\r\n | \r\n | USER PROFILE\r\n | S0: 0\r\n | S3: 13\r\n | S4: 10\r\n | S5: 8\r\n | S6: 2\r\n | S7: 60\r\n | S8: 2\r\n | S10: 15\r\n | +CRLP: 61,61,48,6\r\n | V: 1\r\n | E: 1\r\n | Q: 0\r\n | X: 4\r\n | &C: 1\r\n | &D: 1\r\n | +CLTS: 0\r\n | +CREG: 0\r\n | +CGREG: 0\r\n | +CMEE: 0\r\n |+CIURC: 1\r\n | +CFGRI: 2\r\n | +CMTE: 0\r\n | +CANT: 0,0,10\r\n | +STKPCIS: 0\r\n | +CMGF: 0\r\n | +CNMI: 2,1,0,0,0\r\n | +CSCS: \"IRA\"\r\n | +VTD: 1\r\n | +CALS: 1\r\n | +CHF: 0\r\n | +CAAS: 1\r\n | +CBUZZERRING: 0\r\n | +DDET: 0\r\n | +MORING: 0\r\n | +SVR: 16\r\n | +CCPD: 1\r\n | +CSNS: 0\r\n | +CSGS: 1\r\n | +CNETLIGHT: 1\r\n | +SLEDS: 64,64,64,800,3000,300\r\n | +CSDT: 0\r\n | +CSMINS: 0\r\n | +EXUNSOL:0\r\n | +FSHEX: 0\r\n | +FSEXT: 0\r\n | +IPR: 0\r\n | +IFC: 0,0\r\n | +CSCLK: 0\r\n | \r\n | ACTIVE PROFILE\r\n | S0: 0\r\n | S3: 13\r\n | S4: 10\r\n | S5: 8\r\n | S6: 2\r\n | S7: 60\r\n | S8: 2\r\n | S10: 15\r\n | +CRLP: 61,61,48,6\r\n | V: 1\r\n | E: 1\r\n | Q: 0\r\n | X: 4\r\n | &C: 1\r\n | &D: 1\r\n | +CLTS: 0\r\n | +CREG: 0\r\n | +CGREG: 0\r\n | +CMEE: 0\r\n | +CIURC: 1\r\n | +CFGRI: 2\r\n | +CMTE: 0\r\n | +CANT: 0,0,10\r\n | +STKPCIS: 0\r\n | +CMGF: 0\r\n | +CNMI: 2,1,0,0,0\r\n | +CSCS: \"IRA\"\r\n | +VTD: 1\r\n | +CALS: 1\r\n | +CHF: 0\r\n | +CAAS: 1\r\n | +CBUZZERRING: 0\r\n | +DDET: 0\r\n | +MORING: 0\r\n | +SVR: 16\r\n | +CCPD: 1\r\n | +CSNS: 0\r\n | +CSGS: 1\r\n | +CNETLIGHT: 1\r\n | +SLEDS: 64,64,64,800,3000,300\r\n | +CSDT: 0\r\n | +CSMINS: 0\r\n | +EXUNSOL: 0\r\n | +FSHEX: 0\r\n | +FSEXT: 0\r\n | +IPR:0\r\n | +IFC: 0,0\r\n | +CSCLK: 0\r\n | \r\n | OK\r\n",
"evt_type": "device_config",
"evt_cls": "gsm_consumer"}

{"evt_data": "ERROR",
"evt_type": "sim_imsi",
"evt_cls": "gsm_consumer"}
