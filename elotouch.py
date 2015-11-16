#!/usr/bin/python

import serial
import argparse
import logging

try:
    import uinput
    HAVE_UINPUT = True
except ImportError:
    HAVE_UINPUT = False


DEFAULT_BAUDRATE = 9600

ELO10_LEAD_BYTE = 0x55    # 'U'
ELO10_TOUCH_PACKET = 0x54 # 'T'
ELO10_TOUCH = 0x03

ELO_DATA = None


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
    if HAVE_UINPUT:
        parser.add_argument('--sniff', dest='sniff', required=False, 
                            action="store_true", default=False,
                            help="""Do only listen for packets do not forward to 
                                  event device.""")
                            
    return parser.parse_args()


def argparse_verbosity(parser, default=0):
    parser.add_argument('-v', "--verbose", dest="verbose", action="count",
                        default=default,
                        help="Print out debug and info messages.")
    parser.add_argument('--logfile', dest='logfile', required=False, 
                        type=str, default=None, 
                        help='Give a log file pathname.')                        
    parser.add_argument('--stdout', dest='sout', required=False, 
                        action="store_true", default=False, 
                        help='Output log to standard out.')


def configure_verbosity(args, fmt = '%(message)s'):
    """Configure verbosity for logging.
    
    @param args Parsed arguments from command line.
    @param fmt How the output looks like.
    """    
    if not args.verbose:
        log_level = logging.ERROR
    else:
        if args.verbose == 1:
            log_level = logging.WARNING
        elif args.verbose == 2:
            log_level = logging.INFO
        else:
            log_level = logging.DEBUG

    if args.logfile:
        logging.basicConfig(format=fmt, level=log_level, filename=args.logfile, 
                            filemode="a")
    else:
        logging.basicConfig(format=fmt, level=log_level)

    if args.sout:
        root = logging.getLogger()
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(log_level)
        formatter = logging.Formatter(fmt)
        ch.setFormatter(formatter)
        root.addHandler(ch)


def elo_process_data_10(data):
    global ELO_DATA, ELO_CSUM
    
    if not ELO_DATA:
        if data != ELO10_LEAD_BYTE:
            logging.warning("Got unsynchronized data: 0x%02x\n" % data)
            return
        else:
            logging.debug("Got lead")
            ELO_CSUM = 0xaa
            ELO_DATA = bytearray([data])
    else:
        ELO_DATA.append(data)

    if len(ELO_DATA) != 10:
        ELO_CSUM = (ELO_CSUM + data) & 0xFF
        return
    
    # Process complete message....
    if data != ELO_CSUM:
        logging.warning("bad checksum: 0x%02x, expected 0x%02x", data, ELO_CSUM);
        return
    if ELO_DATA[1] == ELO10_TOUCH_PACKET:
        status = ELO_DATA[2]
        abs_x = (ELO_DATA[4] << 8) | ELO_DATA[3]
        abs_y = (ELO_DATA[6] << 8) | ELO_DATA[5]
        if status & ELO10_TOUCH:
            touch = True
        else:
            touch = False
        abs_z = (ELO_DATA[8] << 8) | ELO_DATA[7]
            
        logging.info("got touch packet, status=0x%02x, touch=%d, abs_x=%d, abs_y=%d, abs_z=%d", status, touch, abs_x, abs_y, abs_z)
        
        #if status & ELO10_PRESSURE:
            #input_report_abs(dev, ABS_PRESSURE, (elo->data[8] << 8) | elo->data[7]);
            #input_report_key(dev, BTN_TOUCH, elo->data[2] & ELO10_TOUCH);
            #input_sync(dev);
            
    ELO_DATA = None
    
            
def main():
    args = parse_arguments()
    configure_verbosity(args)   
    
    try:
        with serial.Serial(args.port, baudrate=args.baud, rtscts=True, timeout=1) as eport:
            logging.info("Port %s successfully opened!", args.port)
            
            while True:
                data = eport.read(1)
                if not len(data):
                    continue
                data = ord(data)
                
                elo_process_data_10(data)
                # ToDo: Add also 6 and 4 byte processing.
         
    except KeyboardInterrupt:
        pass
    except serial.SerialException as e:
        logging.error(e)
        exit(-1)


if __name__ == '__main__':
    main()

