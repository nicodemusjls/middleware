import re
from subprocess import run

DESIGNATION = re.compile(r'(?<=Designation: ).*')
BUS_ADDRESS = re.compile(r'(?<=Bus Address: ).*')
HEX_COLON = re.compile(r'^([0-9a-fA-F][0-9a-fA-F]:){7}[0-9a-fA-F][0-9a-fA-F]$')
NAA_PATTERN = re.compile(r"^naa.[0-9a-fA-F]{16}$")


def wwn_as_colon_hex(hexstr):
    """
    Given a hex string '0xaabbccdd11223344' (or 'naa.aabbccdd11223344')
    return 'aa:bb:cc:dd:11:22:33:44'.
    """
    if isinstance(hexstr, str):
        if hexstr.startswith('0x'):
            # range(2,) to skip the leading 0x
            return ':'.join(hexstr[i:i + 2] for i in range(2, len(hexstr), 2))
        if hexstr.startswith('naa.'):
            # range(4,) to skip the leading naa.
            return ':'.join(hexstr[i:i + 2] for i in range(4, len(hexstr), 2))
        if HEX_COLON.match(hexstr):
            return hexstr


def colon_hex_as_naa(hexstr):
    """
    Given a colon hex string 'aa:bb:cc:dd:11:22:33:44'  return 'naa.aabbccdd11223344'.
    """
    if isinstance(hexstr, str) and HEX_COLON.match(hexstr):
        return 'naa.' + ''.join(hexstr.split(':'))


def str_to_naa(string):
    if isinstance(string, str):
        if string.startswith('0x'):
            return 'naa.' + string[2:]
        if HEX_COLON.match(string):
            return 'naa.' + ''.join(string.split(':')).lower()
        if NAA_PATTERN.match(string):
            return string


def naa_to_int(string):
    if isinstance(string, str) and NAA_PATTERN.match(string):
        return int(f'0x{string[4:]}', 16)


def wwpn_to_vport_naa(wwpn, chan):
    if isinstance(wwpn, str):
        wwpn = naa_to_int(str_to_naa(wwpn))
    if wwpn is None:
        return None
    # Similar to some code in isp_default_wwn (CORE os)
    seed = wwpn
    seed ^= 0x0100000000000000
    seed ^= ((chan + 1) & 0xf) << 56
    seed ^= (((chan + 1) >> 4) & 0xf) << 52
    return str_to_naa(hex(seed))


def dmi_pci_slot_info():
    result = {}
    output = run(['dmidecode', '-t9'], capture_output=True, encoding='utf8').stdout
    for line in output.splitlines():
        if mat := DESIGNATION.search(line):
            designation = mat.group(0)
        if mat := BUS_ADDRESS.search(line):
            bus_addr = mat.group(0)
            result[bus_addr] = designation
    # If any slots are missing a .0 function then fill it in
    additional = {}
    for bus_addr in result:
        if not bus_addr.endswith('.0'):
            new_addr = bus_addr.rsplit('.', 1)[0] + '.0'
            if new_addr not in result:
                additional[new_addr] = result[bus_addr]
    return result | additional


def filter_by_wwpns_hex_string(wwpn_naa, wwpn_b_naa):
    """
    Filter is suitable for consumption by fc.fc_hosts
    """
    if wwpn_naa and wwpn_b_naa:
        return [['OR',
                 [
                     ['port_name', '=', f'0x{wwpn_naa[4:]}'],
                     ['port_name', '=', f'0x{wwpn_b_naa[4:]}'],
                 ]
                 ]]
    elif wwpn_naa:
        return [['port_name', '=', f'0x{wwpn_naa[4:]}']]
    elif wwpn_b_naa:
        return [['port_name', '=', f'0x{wwpn_b_naa[4:]}']]
    else:
        return []


def is_fc_addr(addr):
    if isinstance(addr, str):
        return bool(HEX_COLON.match(addr) or NAA_PATTERN.match(addr))
    return False
