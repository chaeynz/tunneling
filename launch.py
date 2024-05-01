# pylint: disable=missing-docstring
from modules.vti import Tunnel

import time
def main():
    tunnel = Tunnel()
    tunnel.start_listening()
    time.sleep(10)
    tunnel.stop_listening()

if __name__ == "__main__":
    main()