#!/usr/bin/python

import serial
import uinput
import argparse
import logging
#from verbosity import (argparse_verbosity, configure_verbosity)

DEFAULT_BAUDRATE = 9600

ELO10_LEAD_BYTE = 'U'
ELO10_TOUCH_PACKET = 'T'
ELO10_PRESSURE = 0x80
ELO10_TOUCH = 0x03


def parse_arguments():
    """Parse arguments."""
    parser = argparse.ArgumentParser(description="""Runs elotouch driver.""")

    argparse_verbosity(parser)
    parser.add_argument('-p', '--port', dest='port', required=True, type=str,
                        help='Serial port where ELO touch screen is connected to.')
    parser.add_argument('-b', '--baud', dest='baud', type=int, 
                        default=DEFAULT_BAUDRATE,
                        help="""Baudrate to use. 
                                Default is %d.""" % DEFAULT_BAUDRATE)
    parser.add_argument('--sniff', dest='sniff', required=False, 
                        action="store_true", default=False,
                        help="""Do only listen for packets do not forward to 
                              event device.""")
                        
    return parser.parse_args()

        
ELO_DATA = None
        
def elo_process_data_10(data):
    global ELO_DATA, ELO_CSUM
    
    if not ELO_DATA:
        if data != ELO10_LEAD_BYTE:
            logging.warning("Got unsynchronized data: 0x%02x\n" % data)
            return
        else:
            ELO_CSUM = 0xaa
            ELO_DATA = bytearray(data)
    else:
        ELO_DATA.append(data)

    if len(ELO_DATA) != 10:
        ELO_CSUM += data
        return
        
    # Process complete message....
    if data != ELO_CSUM:
        logging.warning("bad checksum: 0x%02x, expected 0x%02x", data, ELO_CSUM);
        return
    if ELO_DATA[1] == ELO10_TOUCH_PACKET:
        abs_x = (ELO_DATA[4] << 8) | ELO_DATA[3]
        abs_y = (ELO_DATA[6] << 8) | ELO_DATA[5]
        logging.info("got touch packet, abs_x=%d, abs_y=%d", abs_x, abs_y)
        
        if ELO_DATA[2] & ELO10_PRESSURE:
            #input_report_abs(dev, ABS_PRESSURE, (elo->data[8] << 8) | elo->data[7]);
            #input_report_key(dev, BTN_TOUCH, elo->data[2] & ELO10_TOUCH);
            #input_sync(dev);
            pass
        ELO_DATA = None
    
            
def main():
    args = parse_arguments()
    #configure_verbosity(args)   
    
    try:
        with serial.Serial(args.port, baudrate=args.baud, timeout=.5) as eport:
            logging.info("Port %s successfully opened!", args.port)
            
            while True:
                data = eport.read(1)
                if not len(data):
                    continue
                elo_process_data_10(data)
                
                    
            
            
    except serial.SerialException, KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()

