#!/usr/bin/python
import sys
import json
from flask import Flask

""" radon_reader.py: RadonEye RD200 (Bluetooth/BLE) Reader """

__progname__    = "RadonEye RD200 (Bluetooth/BLE) Reader"
__version__     = "0.3.6"
__author__      = "Carlos Andre"
__email__       = "candrecn at hotmail dot com"
__date__        = "2019-09-13"

import struct, time, re, json

from bluepy import btle
from time import sleep
from random import randint

app = Flask(__name__)

@app.route('/')
def index():
    address='E4:BC:DC:E5:07:15'
    radon = RetryMultiple(address)

    if radon is not None:
        return json.dumps({'radon': round(radon,2), 'unit': 'pCi/L'})
    else:
        return "error", 500

def RetryMultiple(address, attempts=4):
    try:
        return GetRadonValue(address)

    except Exception as e:
        if args.verbose and not args.silent:
            print (e)
        for i in range(1,attempts):
            try:
                return GetRadonValue(address)
            except:
                if i < attempts-1:
                    continue
                else:
                    return None
            break


def GetRadonValue(address, silent=True, verbose=False):
    if verbose and not silent:
        print ("Connecting...")
    DevBT = btle.Peripheral(address, "random")
    RadonEye = btle.UUID("00001523-1212-efde-1523-785feabcd123")
    RadonEyeService = DevBT.getServiceByUUID(RadonEye)

    # Write 0x50 to 00001524-1212-efde-1523-785feabcd123
    if verbose and not silent:
        print ("Writing...")
    uuidWrite  = btle.UUID("00001524-1212-efde-1523-785feabcd123")
    RadonEyeWrite = RadonEyeService.getCharacteristics(uuidWrite)[0]
    RadonEyeWrite.write(bytes("\x50"))

    # Read from 3rd to 6th byte of 00001525-1212-efde-1523-785feabcd123
    if verbose and not silent:
        print ("Reading...")
    uuidRead  = btle.UUID("00001525-1212-efde-1523-785feabcd123")
    RadonEyeValue = RadonEyeService.getCharacteristics(uuidRead)[0]
    RadonValue = RadonEyeValue.read()
    RadonValue = struct.unpack('<f',RadonValue[2:6])[0]
   
    DevBT.disconnect()

    # Raise exception (will try get Radon value from RadonEye again) if received a very high radon value. 
    # Maybe a bug on RD200 or Python BLE Lib?!
    if RadonValue > 1000:
        raise Exception("Strangely high radon value. Debugging needed.")

    Unit="pCi/L"
 
    if silent:
        #print ("%0.2f" % (RadonValue))
        return RadonValue
    else: 
        print ("%s - %s - Radon Value: %0.2f %s" % (time.strftime("%Y-%m-%d [%H:%M:%S]"),address,RadonValue,Unit))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

