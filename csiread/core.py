"""A fast channel state information parser for Intel, Atheros, Nexmon and
ESP32."""

import os
import numpy as np

from . import _csiread


class Intel(_csiread.Intel):
    """Parse CSI obtained using 'Linux 802.11n CSI Tool'.

    Args:
        file (str or None): CSI data file. If ``str``, ``read`` and ``readstp``
            methods are allowed. If ``None``, ``seek`` and ``pmsg`` methods are
            allowed.
        nrxnum (int, optional): Number of receive antennas. Default: 3
        ntxnum (int, optional): Number of transmit antennas. Default: 2
        pl_size (int, optional): The size of payload to be used. Default: 0
        if_report (bool, optional): Report the parsed result. Default: ``True``
        bufsize (int, optional): The maximum amount of packets to be parsed.
            If ``0`` and file is ``str``, all packets will be parsed. If ``0``
            and file is ``None``, this parameter is ignored by `pmsg` method.
            Default: 0

    Attributes:
        file (str, readonly): CSI data file
        count (int, readonly): Count of 0xbb packets parsed
        timestamp_low (ndarray): The low 32 bits of the NIC's 1 MHz clock. It
            wraps about every 4300 seconds, or 72 minutes.
        bfee_count (ndarray): The count of the total number of beamforming
            measurements that have been recorded by the driver and sent to
            userspace. The netlink channel between the kernel and userspace is
            lossy, so these can be used to detect measurements that were
            dropped in this pipe.
        Nrx (ndarray): The number of antennas used to receive the packet.
        Ntx (ndarray): The number of space/time streams transmitted.
        rssi_a (ndarray): RSSI measured by the receiving NIC at the input to
            antenna port A. This measurement is made during the packet preamble.
            This value is in dB relative to an internal reference.
        rssi_b (ndarray): See ``rssi_a``
        rssi_c (ndarray): See ``rssi_a``
        noise (ndarray): Noise
        agc (ndarray): Automatic Gain Control (AGC) setting in dB
        perm (ndarray): Tell us how the NIC permuted the signals from the 3
            receive antennas into the 3 RF chains that process the measurements.
        rate (ndarray): The rate at which the packet was sent, in the same
            format as the ``rate_n_flags``.
        csi (ndarray): The CSI itself, normalized to an internal reference.
            It is a Count×30×Nrx×Ntx 4-D matrix where the second dimension is
            across 30 subcarriers in the OFDM channel. For a 20 MHz-wide
            channel, these correspond to about half the OFDM subcarriers, and
            for a 40 MHz-wide channel, this is about one in every 4 subcarriers.
        stp (ndarray): World timestamp recorded by the modified ``log_to_file``.
        fc (ndarray): Frame control
        dur (ndarray): Duration
        addr_des (ndarray): Destination MAC address
        addr_src (ndarray): Source MAC address
        addr_bssid (ndarray): BSSID MAC address
        seq (ndarray): Serial number of packet
        payload (ndarray): MAC frame to be used

    Examples:

        >>> csifile = "../material/5300/dataset/sample_0x1_ap.dat"
        >>> csidata = csiread.Intel(csifile, nrxnum=3, ntxnum=2, pl_size=10)
        >>> csidata.read()
        >>> csi = csidata.get_scaled_csi()
        >>> print(csidata.csi.shape)

    References:
        1. `Linux 802.11n CSI Tool <https://dhalperi.github.io/linux-80211n-csitool/>`_
        2. `linux-80211n-csitool-supplementary <https://github.com/dhalperi/linux-80211n-csitool-supplementary>`_
        3. `Linux 802.11n CSI Tool-FAQ <https://dhalperi.github.io/linux-80211n-csitool/faq.html>`_
    """

    def __init__(self, file, nrxnum=3, ntxnum=2, pl_size=0, if_report=True,
                 bufsize=0):
        super(Intel, self).__init__(file, nrxnum, ntxnum, pl_size, if_report,
                                    bufsize)

    def __getitem__(self, index):
        ret = {
            "timestamp_low": self.timestamp_low[index],
            "bfee_count": self.bfee_count[index],
            "Nrx": self.Nrx[index],
            "Ntx": self.Ntx[index],
            "rssi_a": self.rssi_a[index],
            "rssi_b": self.rssi_b[index],
            "rssi_c": self.rssi_c[index],
            "noise": self.noise[index],
            "agc": self.agc[index],
            "perm": self.perm[index],
            "rate": self.rate[index],
            "csi": self.csi[index]
        }
        return ret

    def read(self):
        """Parse data if 0xbb and 0xc1 packets

        Examples:

            >>> csifile = "../material/5300/dataset/sample_0x1_ap.dat"
            >>> csidata = csiread.Intel(csifile)
            >>> csidata.read()
        """
        super().read()

    def seek(self, file, pos, num):
        """Read packets from a specific position

        This method allows us to read different parts of different files
        randomly. It could be useful in Machine Learning. However, it could be
        very slow when reading files in HDD for the first time. For this case,
        it is better to do a pre-read with ``read()`` first.

        Args:
            file (str): CSI data file.
            pos (int): Position of file descriptor corresponding to the packet.
                Currently, it must be returned by the function in
                ``example/csiseek.py``.
            num (int): Number of packets to be read. ``num <= bufsize`` must be
                true. If ``0``, all packets after ``pos`` will be read.

        Examples:

            >>> csifile = "../material/5300/dataset/sample_0x1_ap.dat"
            >>> csidata = csiread.Intel(None, bufsize=16)
            >>> for i in range(10):
            >>>     csidata.seek(csifile, 0, i+1)
            >>>     print(csidata.csi.shape)
        """
        super().seek(file, pos, num)

    def pmsg(self, data):
        """Parse message in real time

        Args:
            data (bytes): A bytes object representing the data received by udp
                socket
        Returns:
            int: The status code. If ``0xbb`` and ``0xc1``, parse message
                successfully. Otherwise, the ``data`` is not a CSI packet.

        Examples:

            >>> import socket
            >>> import csiread
            >>>
            >>> csidata = csiread.Intel(None)
            >>> with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            >>>     s.bind(('127.0.0.1', 10011))
            >>>     while True:
            >>>         data, address_src = s.recvfrom(4096)
            >>>         code = csidata.pmsg(data)
            >>>         if code == 0xbb:
            >>>             print(csidata.csi.shape)
        """
        return super().pmsg(data)

    def readstp(self, endian='little'):
        """Parse timestamp recorded by the modified ``log_to_file``

        ``file.dat`` and ``file.datstp`` must be in the same directory.

        Args:
            endian (str): The byte order of ``file.datstp``， it can be
                ``little`` and ``big``. Default: ``little``

        Returns:
            int: Timestamp of the first packet.

        Examples:

            >>> csifile = "../material/5300/dataset/sample_0x1_ap.dat"
            >>> csidata = csiread.Intel(csifile)
            >>> first_stp = csidata.readstp()
            >>> print(first_stp)
        """
        return super().readstp(endian)

    def get_total_rss(self):
        """Calculate the Received Signal Strength[RSS] in dBm from CSI

        Examples:

            >>> csifile = "../material/5300/dataset/sample_0x1_ap.dat"
            >>> csidata = csiread.Intel(csifile)
            >>> csidata.read()
            >>> rssi = csidata.get_total_rss()
            >>> print(rssi.shape)
        """
        return super().get_total_rss()

    def get_scaled_csi(self, inplace=False):
        """Convert CSI to channel matrix H

        Args:
            inplace (bool): Optionally do the operation in-place. Default: False

        Returns:
            ndarray: Channel matrix H

        Examples:

            >>> csifile = "../material/5300/dataset/sample_0x1_ap.dat"
            >>> csidata = csiread.Intel(csifile)
            >>> csidata.read()
            >>> scaled_csi = csidata.get_scaled_csi(False)
            >>> print(scaled_csi.shape)
            >>> print("scaled_csi is csidata.csi: ", scaled_csi is csidata.csi)
        """
        return super().get_scaled_csi(inplace)

    def get_scaled_csi_sm(self, inplace=False):
        """Convert CSI to pure channel matrix H

        This version undoes Intel's spatial mapping to return the pure MIMO
        channel matrix H.

        Args:
            inplace (bool): Optionally do the operation in-place. Default: False

        Returns:
            ndarray: The pure MIMO channel matrix H.

        Examples:

            >>> csifile = "../material/5300/dataset/sample_0x1_ap.dat"
            >>> csidata = csiread.Intel(csifile)
            >>> csidata.read()
            >>> scaled_csi_sm = csidata.get_scaled_csi_sm(False)
            >>> print(scaled_csi.shape)
            >>> print("scaled_csi_sm is csidata.csi: ", scaled_csi_sm is csidata.csi)
        """
        return super().get_scaled_csi_sm(inplace)

    def apply_sm(self, scaled_csi):
        """Undo the input spatial mapping

        Args:
            scaled_csi (ndarray): Channel matrix H.

        Returns:
            ndarray: The pure MIMO channel matrix H.

        Examples:

            >>> csifile = "../material/5300/dataset/sample_0x1_ap.dat"
            >>> csidata = csiread.Intel(csifile)
            >>> csidata.read()
            >>> scaled_csi = csidata.get_scaled_csi()
            >>> scaled_csi_sm = csidata.apply_sm(scaled_csi)
            >>> print(scaled_csi_sm.shape)
        """
        return super().apply_sm(scaled_csi)


class Atheros(_csiread.Atheros):
    """Parse CSI obtained using 'Atheros CSI Tool'.

    Args:
        file (str or None): CSI data file. If ``str``, ``read`` and ``readstp``
            methods are allowed. If ``None``, ``seek`` and ``pmsg`` methods are
            allowed.
        nrxnum (int, optional): Number of receive antennas. Default: 3
        ntxnum (int, optional): Number of transmit antennas. Default: 2
        pl_size (int, optional): The size of payload to be used. Default: 0
        tones (int, optional): The number of subcarrier. It can be 56 and 114.
            Default: 56
        if_report (bool, optional): Report the parsed result. Default: ``True``
        bufsize (int, optional): The maximum amount of packets to be parsed.
            If ``0`` and file is ``str``, all packets will be parsed. If ``0``
            and file is ``None``, this parameter is ignored by ``pmsg`` method.
            Default: 0

    Attributes:
        file (str, readonly): CSI data file
        count (int, readonly): Count of CSI packets parsed
        timestamp (ndarray): The time when packet is received, expressed in μs
        csi_len (ndarray): The csi data length in the received data buffer,
            expressed in bytes
        tx_channel (ndarray): The center frequency of the wireless channel,
            expressed in MHz
        err_info (ndarray): The phy error code, set to 0 if correctly received
        noise_floor (ndarray): The noise floor, expressed in dB. But it needs
            to be update and is set to 0 in current version.
        Rate (ndarray): The data rate of the received packet. Its value is a
            unsigned 8 bit integer number and the mapping between this value
            and the rate choice of 802.11 protocol
        bandWidth (ndarray): The channel bandwidth. It is 20MHz if set to 0 and
            40MHz if set to 1
        num_tones (ndarray): The number of subcarrier that used for data
            transmission.
        nr (ndarray): Number of receiving antenna
        nc (ndarray): Number of transmitting antenna
        rsssi (ndarray): The rssi of combination of all active chains
        rssi_1 (ndarray): The rssi of active chain 0
        rssi_2 (ndarray): The rssi of active chain 1
        rssi_3 (ndarray): The rssi of active chain 2
        payload_len (ndarray): The payload length of received packet, expressed
            in bytes.
        csi (ndarray): CSI
        payload (ndarray): MAC frame(MPDU) to be used

    Examples:

        >>> csifile = "../material/atheros/dataset/ath_csi_1.dat"
        >>> csidata = csiread.Atheros(csifile, nrxnum=3, ntxnum=2, pl_size=10, tones=56)
        >>> csidata.read(endian='little')
        >>> print(csidata.csi.shape)

    References:
        1. `Atheros CSI Tool <https://wands.sg/research/wifi/AtherosCSI/>`_
        2. `Atheros-CSI-Tool-UserSpace-APP <https://github.com/xieyaxiongfly/Atheros-CSI-Tool-UserSpace-APP>`_
        3. `Atheros CSI Tool User Guide <https://wands.sg/research/wifi/AtherosCSI/document/Atheros-CSI-Tool-User-Guide.pdf>`_
    """

    def __init__(self, file, nrxnum=3, ntxnum=2, pl_size=0, tones=56,
                 if_report=True, bufsize=0):
        super(Atheros, self).__init__(file, nrxnum, ntxnum, pl_size, tones,
                                      if_report, bufsize)

    def __getitem__(self, index):
        ret = {
            "timestamp": self.timestamp[index],
            "csi_len": self.csi_len[index],
            "tx_channel": self.tx_channel[index],
            "err_info": self.err_info[index],
            "noise_floor": self.noise_floor[index],
            "Rate": self.Rate[index],
            "bandWidth": self.bandWidth[index],
            "num_tones": self.num_tones[index],
            "nr": self.nr[index],
            "nc": self.nc[index],
            "rssi": self.rssi[index],
            "rssi_1": self.rssi_1[index],
            "rssi_2": self.rssi_2[index],
            "rssi_3": self.rssi_3[index],
            "payload_len": self.payload_len[index],
            "csi": self.csi[index],
            "payload": self.payload[index]
        }
        return ret

    def read(self, endian='little'):
        """Parse data

        Args:
            endian (str): The byte order of ``file.dat``， it can be ``little``
                and ``big``. Default: ``little``

        Examples:

            >>> csifile = "../material/atheros/dataset/ath_csi_1.dat"
            >>> csidata = csiread.Atheros(csifile)
            >>> csidata.read()
        """
        super().read(endian)

    def seek(self, file, pos, num, endian='little'):
        """Read packets from a specific position

        This method allows us to read different parts of different files
        randomly. It could be useful in Machine Learning. However, it could be
        very slow when reading files in HDD for the first time. For this case,
        it is better to do a pre-read with ``read()`` first.

        Args:
            file (str): CSI data file.
            pos (int): Position of file descriptor corresponding to the packet.
                Currently, it must be returned by the function in
                `example/csiseek.py`.
            num (int): Number of packets to be read. ``num <= bufsize`` must be
                true. If ``0``, all packets after ``pos`` will be read.
            endian (str): The byte order of ``file.dat``， it can be ``little``
                and ``big``. Default: ``little``

        Examples:

            >>> csifile = "../material/atheros/dataset/ath_csi_1.dat"
            >>> csidata = csiread.Atheros(None, bufsize=16)
            >>> for i in range(10):
            >>>     csidata.seek(csifile, 0, i+1)
            >>>     print(csidata.csi.shape)
        """
        super().seek(file, pos, num, endian)

    def pmsg(self, data, endian='little'):
        """Parse message in real time

        Args:
            data (bytes): A bytes object representing the data received by udp
                socket
            endian (str): The byte order of ``file.dat``， it can be ``little``
                and ``big``. Default: ``little``

        Returns:
            int: The status code. If ``0xff00``, parse message successfully.
                Otherwise, the ``data`` is not a CSI packet.

        Examples:

            >>> import socket
            >>> import csiread
            >>>
            >>> csidata = csiread.Atheros(None)
            >>> with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            >>>     s.bind(('127.0.0.1', 10011))
            >>>     while True:
            >>>         data, address_src = s.recvfrom(4096)
            >>>         code = csidata.pmsg(data)
            >>>         if code == 0xff00:
            >>>             print(csidata.csi.shape)
        """
        return super().pmsg(data, endian)

    def readstp(self, endian='little'):
        """Parse timestamp recorded by the modified ``recv_csi``

        ``file.dat`` and ``file.datstp`` must be in the same directory.

        Args:
            endian (str): The byte order of ``file.datstp``， it can be
                ``little`` and ``big``. Default: ``little``

        Examples:

            >>> csifile = "../material/atheros/dataset/ath_csi_1.dat"
            >>> csidata = csiread.Atheros(csifile)
            >>> first_stp = csidata.readstp()
            >>> print(first_stp)
        """
        return super().readstp(endian)


class Nexmon(_csiread.Nexmon):
    """Parse CSI obtained using 'nexmon_csi'.

    Args:
        file (str or None): CSI data file ``.pcap``. If ``str``, ``read``
            methods is allowed. If ``None``, ``seek`` and ``pmsg`` methods are
            allowed.
        chip (str): WiFi Chip, it can be '4339', '43455c0', '4358' and '4366c0'.
        bw (int): bandwidth, it can be 20, 40 and 80.
        if_report (bool, optional): Report the parsed result. Default: `True`
        bufsize (int, optional): The maximum amount of packets to be parsed. If
            ``0`` and file is ``str``, all packets will be parsed. If ``0`` and
            file is ``None``, this parameter is ignored by `pmsg` method.
            Default: 0

    Attributes:
        file (str, readonly): CSI data file
        count (int, readonly): Count of csi packets parsed
        chip (str, readonly): Chip type we set
        bw (int, readonly): Bandwidth we set
        nano (bool, readonly): nanosecond-resolution or not
        sec (ndarray): Time the packet was captured
        usec (ndarray): The microseconds when this packet was captured, as an
            offset to ``sec`` if ``nano`` is True. The nanoseconds when the
            packet was captured, as an offset to ``sec`` if ``nano`` is False.
        caplen (ndarray): The number of bytes of packet data actually captured
            and saved in the file
        wirelen (ndarray): The length of the packet as it appeared on the
            network when it was captured
        magic (ndarray): Four magic bytes ``0x11111111``
        src_addr (ndarray): Source MAC address
        seq (ndarray): Sequence number of the Wi-Fi frame that triggered the
            collection of the CSI contained in packets
        core (ndarray): Core
        spatial (ndarray): Spatial stream
        chan_spec (ndarray): (unknown)
        chip_version (ndarray): The chip version
        csi (ndarray): CSI

    Examples:

        >>> csifile = "../material/nexmon/dataset/example.pcap"
        >>> csidata = csiread.Nexmon(csifile, chip='4358', bw=80)
        >>> csidata.read()
        >>> print(csidata.csi.shape)

    References:
        1. `nexmon_csi <https://github.com/seemoo-lab/nexmon_csi>`_
        2. `rdpcap <https://github.com/secdev/scapy/blob/master/scapy/utils.py>`_
        3. `Libpcap File Format <https://wiki.wireshark.org/Development/LibpcapFileFormat>`_
    """
    def __init__(self, file, chip, bw, if_report=True, bufsize=0):
        super(Nexmon, self).__init__(file, chip, bw, if_report, bufsize)

    def __getitem__(self, index):
        ret = {
            "magic": self.magic[index],
            "src_addr": self.src_addr[index],
            "seq": self.seq[index],
            "core": self.core[index],
            "spatial": self.spatial[index],
            "chan_spec": self.chan_spec[index],
            "chip_version": self.chip_version[index],
            "csi": self.csi[index]
        }
        return ret

    def read(self):
        """Parse data

        Examples:

            >>> csifile = "../material/nexmon/dataset/example.pcap"
            >>> csidata = csiread.Nexmon(csifile, chip='4358', bw=80)
            >>> csidata.read()
            >>> print(csidata.csi.shape)
        """
        super().read()

    def seek(self, file, pos, num):
        """Read packets from specific position

        This method allows us to read different parts of different files
        randomly. It could be useful in Machine Learning. However, it could be
        very slow when reading files in HDD for the first time. For this case,
        it is better to use `read()` for a pre-read first.

        Args:
            file (str): CSI data file ``.pcap``.
            pos (int): Position of file descriptor corresponding to the packet.
                Currently, it must be returned by the function in 
                ``example/csiseek.py``.
            num (int): Number of packets to be read. ``num <= bufsize`` must be
                true. If ``0``, all packets after ``pos`` will be read.

        Examples:

            >>> csifile = "../material/nexmon/dataset/example.pcap"
            >>> csidata = csiread.Nexmon(None, chip='4358', bw=80, bufsize=4)
            >>> for i in range(4):
            >>>     csidata.seek(csifile, 0, i+1)
            >>>     print(csidata.csi.shape)
        """
        super().seek(file, pos, num)

    def pmsg(self, data, endian='little'):
        """Parse message in real time

        Args:
            data (bytes): A bytes object representing the data received by udp
                socket
            endian (str): The byte order of ``file.dat``， it can be ``little``
                and ``big``. Default: ``little``

        Returns:
            int: The status code. If ``0xf100``, parse message successfully.
                Otherwise, the ``data`` is not a CSI packet.

        Examples:

            >>> import socket
            >>> import csiread
            >>> 
            >>> csidata = csiread.Nexmon(None, chip='4358', bw=80)
            >>> with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            >>>     s.bind(('127.0.0.1', 10011))
            >>>     while True:
            >>>         data, address_src = s.recvfrom(4096)
            >>>         code = csidata.pmsg(data)
            >>>         if code == 0xf100:
            >>>             print(csidata.csi.shape)
        """
        return super().pmsg(data, endian)

    def group(self, c_num=4, s_num=4):
        """Build spatial stream index (experimental)

        There are 2 steps:

        1. Combine adjacent packets with the same sequence number into a frame.
        2. Permute the order of antennas in each frame

        Step 1 drops the broken frames. Step 2 doesn't work if core and spatial
        are unknown.

        Args:
            c_num (int): the number of core. Default: 4
            s_num (int): the number of spatial. Default: 4

        Returns:
            ndarray: offset, the position of frames.
                shape=[frame_count, c_num, s_num]

        Examples:

            >>> offset = csidata.group(4, 4)
            >>> csi = csidata.csi[offset]
            >>> sec = csidata.sec[offset]
        """
        return _nex_group(self.seq, self.core, self.spatial, s_num, c_num)


class AtherosPull10(Atheros):
    """Parse CSI obtained using 'Atheros CSI Tool' pull 10.

    The same as Atheros

    References:
        1. `Atheros-CSI-Tool-UserSpace-APP pull 10 <https://github.com/xieyaxiongfly/Atheros-CSI-Tool-UserSpace-APP/pull/10>`_
    """
    def read(self):
        """Parse data

        Examples:

            >>> csifile = "../material/atheros/dataset/ath_csi_1.dat"
            >>> csidata = csiread.Atheros(csifile)
            >>> csidata.read()
        """
        with open(self.file, 'rb') as f:
            endian = 'big' if f.read(1) == b'\xff' else 'little'
        self.seek(self.file, 1, 0, endian)


class NexmonPull46(_csiread.NexmonPull46):
    """Parse CSI obtained using 'nexmon_csi' pull 46.

    Args:
        See ``Nexmon``

    Attributes:
        _autoscale (int): It can be 0 and 1, Pull 46 set it to 0. If you got a
            bad plotting, you may want it to be 1.
        rssi (ndarray): rssi
        fc (ndarray): frame control
        others: see ``Nexmon``

    References:
        1. `nexmon_csi pull 46 <https://github.com/seemoo-lab/nexmon_csi/pull/46>`_
    """
    def __init__(self, file, chip, bw, if_report=True, bufsize=0):
        super(NexmonPull46, self).__init__(file, chip, bw, if_report, bufsize)
        self._autoscale = 0     # Undetermined

    def __getitem__(self, index):
        ret = {
            "magic": self.magic[index],
            "rssi": self.rssi[index],
            "fc": self.fc[index],
            "src_addr": self.src_addr[index],
            "seq": self.seq[index],
            "core": self.core[index],
            "spatial": self.spatial[index],
            "chan_spec": self.chan_spec[index],
            "chip_version": self.chip_version[index],
            "csi": self.csi[index]
        }
        return ret

    def pmsg(self, data, endian='little'):
        """Parse message in real time

        Args:
            data (bytes): A bytes object representing the data received by udp
                socket
            endian (str): The byte order of ``file.dat``， it can be ``little``
                and ``big``. Default: ``little``

        Returns:
            int: The status code. If ``0xf101``, parse message successfully.
                Otherwise, the ``data`` is not a CSI packet.
        """
        return super().pmsg(data, endian)

    def group(self, c_num=4, s_num=4):
        """Build spatial stream index (experimental)

        See `Nexmon.group`
        """
        return _nex_group(self.seq, self.core, self.spatial, s_num, c_num)


class ESP32:
    """Parse CSI obtained using 'ESP32-CSI-Tool'.(experimental)

    For better flexibility, please consider ``pandas.read_csv``

    Args:
        file (str or None): CSI data file ``.csv``. If ``str``, ``read``
            methods is allowed. If ``None``, ``seek`` and ``pmsg`` methods are
            allowed.
        if_report (bool, optional): Report the parsed result. Default: `True`
        csi_only (bool, optional): Only parse csi and ignore the others.
            Default: `False`.
        maxlen (int, optional): The max length of csi_data filed. Designed for
            the issue #12 of ESP32-CSI-Tool. Default: `128`.

    Attributes:
        pass

    References:
        1. `ESP32-CSI-Tool <https://github.com/StevenMHernandez/ESP32-CSI-Tool>`_
    """
    def __init__(self, file, if_report=True, csi_only=False, maxlen=128):
        self.file = file
        self.if_report = if_report
        self.csi_only = csi_only
        self.maxlen = maxlen
        self.dt = {'csi': list} if csi_only else \
                  {'type': str, 'role': str, 'mac': str, 'rssi': int,
                   'rate': int, 'sig_mode': int, 'mcs': int, 'bandwidth': int,
                   'smoothing': int, 'not_sounding': int, 'aggregation': int,
                   'stbc': int, 'fec_coding': int, 'sgi': int,
                   'noise_floor': int, 'ampdu_cnt': int, 'channel': int,
                   'secondary_channel': int, 'local_timestamp': int, 'ant': int,
                   'sig_len': int, 'rx_state': int, 'real_time_set': int,
                   'real_timestamp': float, 'len': int, 'csi': list}
        self.dt_str = [k for k, v in self.dt.items() if v is str]
        self.dt_int = [k for k, v in self.dt.items() if v is int]
        self.dt_flo = [k for k, v in self.dt.items() if v is float]
        self.dt_csi = [k for k, v in self.dt.items() if v is list]
        for k in self.dt.keys():
            self.__setattr__(k, None)

    def __getitem__(self, index):
        ret = {k: self.__getattribute__(k)[index] for k in self.dt.keys()}
        return ret

    def read(self):
        """Parse data

        Examples:

            >>> csifile = "../material/esp32/dataset/example_csi.csv"
            >>> csidata = csiread.ESP32(csifile)
            >>> csidata.read()
            >>> print(csidata.csi.shape)
        """
        self.seek(self.file, 0, 0)
        if self.if_report:
            print("%d packets parsed" % self.count)

    def seek(self, file, pos, num):
        """Read packets from specific position

        This method allows us to read different parts of different files
        randomly. It could be useful in Machine Learning. However, it could be
        very slow when reading files in HDD for the first time. For this case,
        it is better to use `read()` for a pre-read first.

        Args:
            file (str): CSI data file ``.csv``.
            pos (int): Position of file descriptor corresponding to the packet.
                Currently, it must be returned by the function in
                ``example/csiseek.py``.
            num (int): Number of packets to be read. If ``0``, all packets
                after ``pos`` will be read.

        Examples:

            >>> csifile = "../material/esp32/dataset/example_csi.csv"
            >>> csidata = csiread.ESP32(None)
            >>> for i in range(4):
            >>>     csidata.seek(csifile, 0, i+1)
            >>>     print(csidata.csi.shape)
        """
        if num == 0:
            num = np.iinfo(np.int).max
        count = 0
        str_data = [[], [], []]
        int_data, flo_data, csi_data = [], [], []

        with open(file) as f:
            f.seek(pos, os.SEEK_CUR)
            for line in f:
                if count >= num:
                    break

                if self.csi_only:
                    line = line.split(',[')
                else:
                    line = line.split(',')
                    line[23], line[24] = line[24], line[23]
                    str_data[0].append(line[0])
                    str_data[1].append(line[1])
                    str_data[2].append(line[2])
                    int_data.append(' '.join(line[3:24]))
                    flo_data.append(line[24])

                line_csi = line[-1][:-2].lstrip('[')
                csi_data.append(line_csi)
                if self.maxlen != 128:
                    ph_num = self.maxlen - line_csi.count(' ')
                    csi_data.append(ph_num * ' 0')
                count += 1

        int_data = ' '.join(int_data)
        flo_data = ' '.join(flo_data)
        csi_data = ' '.join(csi_data)
        self.__parse(str_data, int_data, flo_data, csi_data, count)

    def pmsg(self, data):
        """Parse message in real time

        Args:
            data (string): A string object representing the data received by
                pipe

        Returns:
            int: The status code. If ``0xf200``, parse message successfully.
                Otherwise, the ``data`` is not a CSI packet.

        Examples:

            >>> import sys
            >>> 
            >>> csidata = ESP32(None, False)
            >>> while True:
            >>>     data = sys.stdin.readline().strip('\n')
            >>>     code = csidata.pmsg(data)
            >>>     if code == 0xf200:
            >>>         print(csidata.csi.shape)
        """
        if data.startswith('CSI_DATA'):
            if self.csi_only:
                line = data.split(',[')
            else:
                line = data.split(',')
                str_data = [[li] for li in line[:3]]
                int_data = ' '.join(line[3:23] + line[24:25])
                flo_data = ' '.join(line[23:24])
            csi_data = line[-1][:-2].lstrip('[')
            if self.maxlen != 128:
                ph_num = self.maxlen - csi_data.count(' ')
                csi_data = csi_data + ph_num * ' 0'
            self.__parse(str_data, int_data, flo_data, csi_data, 1)
            return 0xf200

    def __parse(self, str_data, int_data, flo_data, csi_data, count):
        str_array = str_data
        int_array = np.fromstring(int_data, int, sep=' ').reshape(count, -1)
        flo_array = np.fromstring(flo_data, float, sep=' ').reshape(count, -1)
        csi_array = np.fromstring(csi_data, int, sep=' ').reshape(count, -1)

        for idx, k in enumerate(self.dt_str):
            self.__setattr__(k, str_array[idx])
        for idx, k in enumerate(self.dt_int):
            self.__setattr__(k, int_array[:, idx])
        for idx, k in enumerate(self.dt_flo):
            self.__setattr__(k, flo_array[:, idx])
        for idx, k in enumerate(self.dt_csi):
            self.__setattr__(k, csi_array[:, 1::2] + csi_array[:, ::2] * 1.j)
        self.count = count


def _nex_group(seq, core, spatial, c_num=4, s_num=4):
    """Build spatial stream index"""
    # step 1
    ant_num = c_num * s_num
    seq_diff = np.diff(seq)
    offset = np.where(seq_diff != 0)[0]
    offset = np.r_[0, offset + 1]
    count = np.diff(np.r_[offset, len(seq)])
    offset = offset[count == ant_num]
    offset = offset[:, None] + np.r_[:ant_num]

    # step 2
    core = core[offset]
    spatial = spatial[offset]
    p = core * s_num + spatial
    p = np.argsort(p, axis=-1)
    offset = offset[:, :1] + p
    offset = offset.resahpe(-1, c_num, s_num)

    return offset
