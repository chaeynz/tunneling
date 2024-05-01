# pylint: disable=missing-docstring
import os
import fcntl
import struct
import threading
import errno


from modules.event_handler import Event, EventHandler

TUNSETIFF = 0x400454ca # ioctl command used to configure TUN or TAP device. Tells the ioctl syscall that the operation will be setting the flags and parameters for TUN/TAP device
IFF_TUN = 0x0001 # This flag is used to specify that the device being manipulated is a TUN device
IFF_NO_PI = 0x1000 # Normally TUN/TAP devices can prepend a header to each packet with meta information such as flags and the protocol. Disabling this simplifies packet processing


class Tunnel:
    def __init__(self):
        self._tun, self.ifr = self.get_vti()
        self._handler = EventHandler()
        self._stop_event = threading.Event()
        self.set_non_blocking(self._tun)

    def __del__(self):
        if self._listen_thread.is_alive():
            self.stop_listening()
        os.close(self._tun)

    def get_vti(self):
        """
        returns tun, ifr
        """
        return os.open('/dev/net/tun', os.O_RDWR), struct.pack('16sH', b'tun0', IFF_TUN | IFF_NO_PI)
        # Pack into binary format
        # '16sH' = 16-byte string followed by an unsigned short integer
        # b'tun0' = Byte String for the interface name
        # IFF_TUN = TUN device is being used, as opposed to a TAP device, TUN=Layer3;TAP=Layer2
        # IFF_NO_PI = Packet Information tells the system not to provide packet information on read/write 

    def set_non_blocking(self, fd):
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    def encapsulate(self):
        pass

    def deencapsulate(self):
        pass

    def start_listening(self):
        fcntl.ioctl(self._tun, TUNSETIFF, self.ifr)

        def listen():
            while not self._stop_event.is_set():
                try:
                    packet = os.read(self._tun, 2048)
                    if packet:
                        self._handler.notify(Event.MESSAGE_RECV, packet)

                except OSError as e:
                    if e.errno == errno.EAGAIN:
                        continue
                    print(f'Failed to read from device: {e}')
                    break

        self._listen_thread:threading.Thread = threading.Thread(target=listen)
        self._listen_thread.daemon = True
        self._listen_thread.start()

    def stop_listening(self):
        self._stop_event.set()
        self._listen_thread.join()
