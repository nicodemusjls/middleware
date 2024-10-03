from dataclasses import dataclass
from types import MappingProxyType

from .exceptions import DataLengthError, FileTooShort, MismatchHeaderType


class InvalidDescriptorDataLength(Exception): ...


@dataclass(slots=True, frozen=True)
class Pg83:
    periph_type: MappingProxyType = MappingProxyType(
        {
            0: 
        }
    )
    association: MappingProxyType = MappingProxyType(
        {
            0: "Addressed Logical Unit",
            1: "Target Port",
            2: "Target Device",
            3: "Reserved",
        }
    )
    designator_type: MappingProxyType = MappingProxyType(
        {
            0: "Vendor Specific",
            1: "T10 Vendor ID",
            2: "EUI-64",
            3: "NAA",
            4: "Relative Target Port",
            5: "Target Port Group",
            6: "Logical Unit Group",
            7: "MD5 Logical Unit",
            8: "SCSI Name String",
            9: "Protocol Specific Port",
            10: "UUID",
        }
    )
    code_set: MappingProxyType = MappingProxyType({1: "Binary", 2: "ASCII", 3: "UTF-8"})

    @property
    def parse_it(self, file_path):
        with open(file_path, "rb") as f:
            header = memoryview(f.read(4))
            if header.nbytes < 4:
                raise FileTooShort("File too short for VPD Page 0x83.")

            if header[1] != 0x83:
                raise MismatchHeaderType(
                    f"Unexpected page code: {hex(header[1])}, expected 0x83."
                )

            peripheral_device_type = header[0] & 0b00011111  # bits 0-4
            peripheral_qualifier = (header[0] >> 5) & 0b00000111  # bits 5-7

            page_length = int.from_bytes(header[2:4], byteorder="big")
            data = memoryview(f.read(page_length))
            len_data = len(data)
            if len_data < page_length:
                raise DataLengthError("Data length less than page length.")

            offset = 0
            while offset < len_data:
                end = offset + 4
                if end > len_data:
                    raise InvalidDescriptorDataLength(
                        "Not enough data for descriptor header."
                    )

                descriptor_header = data[offset:end]
                code_set = descriptor_header[0] & 0x0F  # Bits 3-0
                piv = (descriptor_header[0] & 0x10) >> 4  # Bit 4
                protocol_identifier = (descriptor_header[0] & 0xF0) >> 4  # Bits 7-4

                # Byte 1
                association = (descriptor_header[1] & 0x30) >> 4  # Bits 5-4
                identifier_type = descriptor_header[1] & 0x0F  # Bits 3-0

                # Byte 3
                identifier_length = descriptor_header[3]
                identifier_offset = offset + 4
                identifier_end = identifier_offset + identifier_length

                if identifier_end > len(data):
                    print("Error: Not enough data for identifier.")
                    break

                identifier = data[identifier_offset:identifier_end]

                # Determine code set and decode identifier accordingly
                id_str = ""
                if identifier_type == 3:  # NAA
                    id_str = decode_naa_identifier(identifier)
                elif code_set == 1:  # Binary
                    id_str = identifier.hex().upper()
                elif code_set == 2:  # ASCII
                    id_str = identifier.decode("ascii", errors="replace").strip()
                elif code_set == 3:  # UTF-8
                    id_str = identifier.decode("utf-8", errors="replace").strip()
                else:
                    id_str = identifier.hex().upper()

                # Get human-readable names
                association_name = self.association.get(
                    association, f"Unknown ({association})"
                )
                identifier_type_name = IDENTIFIER_TYPE_MAP.get(
                    identifier_type, f"Unknown ({identifier_type})"
                )
                code_set_name = CODE_SET_MAP.get(code_set, f"Unknown ({code_set})")

                # Print descriptor information
                print(f"\n{association_name} Identifier ({identifier_type_name}):")
                print(f"  Code Set: {code_set_name}")
                print(f"  PIV: {piv}")
                print(f"  Identifier Type: {identifier_type} ({identifier_type_name})")
                print(f"  Identifier Length: {identifier_length}")
                print(f"  Identifier: {id_str}")

                # Move to the next descriptor
                offset = identifier_end


def decode_naa_identifier(identifier):
    # NAA identifier formats according to the SCSI SPC standard
    if len(identifier) < 8:
        return identifier.hex().upper()

    naa_type = (identifier[0] & 0xF0) >> 4
    naa_formats = {
        0x2: "IEEE Extended",
        0x3: "Locally Assigned",
        0x5: "IEEE Registered",
        0x6: "IEEE Registered Extended",
    }

    naa_format = naa_formats.get(naa_type, f"Unknown ({naa_type})")
    formatted_identifier = identifier.hex().upper()
    return f"NAA {naa_type} ({naa_format}): {formatted_identifier}"
