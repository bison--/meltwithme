#!/usr/bin/env python3

import sys
import fcntl

def decrypt(key: list[int], data: list[int]) -> list[int]:
    cstate  = [0x48, 0x74, 0x65, 0x6D, 0x70, 0x39, 0x39, 0x65]
    shuffle = [2, 4, 0, 7, 1, 6, 5, 3]

    # Phase 1: un-shuffle
    phase1 = [0] * 8
    for i, o in enumerate(shuffle):
        phase1[o] = data[i]

    # Phase 2: key XOR
    phase2 = [phase1[i] ^ key[i] for i in range(8)]

    # Phase 3: bit-rotation
    phase3 = [((phase2[i] >> 3) | (phase2[(i - 1) % 8] << 5)) & 0xFF
              for i in range(8)]

    # Prepare ctmp by nibble-swap
    ctmp = [((cstate[i] >> 4) | (cstate[i] << 4)) & 0xFF
            for i in range(8)]

    # Final subtract-and-wrap
    out = [ (0x100 + phase3[i] - ctmp[i]) & 0xFF
            for i in range(8) ]

    return out

def hd(d: list[int]) -> str:
    return " ".join(f"{e:02X}" for e in d)

def main():
    #if len(sys.argv) != 2:
    #    print(f"Usage: {sys.argv[0]} <device>", file=sys.stderr)
    #    sys.exit(1)
    device_path = '/dev/hidraw22'
    if len(sys.argv) >= 2:
        device_path = sys.argv[1]

    # Key retrieved from /dev/random, guaranteed to be random ;)
    key = [0xC4, 0xC6, 0xC0, 0x92, 0x40, 0x23, 0xDC, 0x96]

    # Open device for read/write in binary, no buffering
    with open(device_path, "a+b", buffering=0) as fp:
        # HID feature-report ioctl code
        HIDIOCSFEATURE_9 = 0xC0094806

        # Prepend report ID (0) to the 8-byte key
        report = bytes([0] + key)
        fcntl.ioctl(fp, HIDIOCSFEATURE_9, report)

        values: dict[int, int] = {}

        while True:
            chunk = fp.read(8)
            if not chunk or len(chunk) < 8:
                # EOF or short read; exit cleanly
                break

            data = list(chunk)  # each element is already an int 0–255
            decrypted = decrypt(key, data)

            # Validate checksum: decrypted[4] should be 0x0D
            # and sum(decrypted[0:3])&0xFF == decrypted[3]
            if decrypted[4] != 0x0D or ((sum(decrypted[:3]) & 0xFF) != decrypted[3]):
                print(f"{hd(data)}  =>  {hd(decrypted)}  Checksum error")
                continue

            op  = decrypted[0]
            val = (decrypted[1] << 8) | decrypted[2]
            values[op] = val

            # Print all known values, marking the newly updated one with '*'
            parts = []
            for k in sorted(values):
                mark = "*" if k == op else " "
                parts.append(f"{mark}{k:02X}:{values[k]:04X} {values[k]:5d}")
            print(", ".join(parts), end="   ")

            # From http://co2meters.com/Documentation/AppNotes/AN146-RAD-0401-serial-communication.pdf
            if 0x50 in values:
                print(f"CO2: {values[0x50]:4d}", end="   ")
            if 0x42 in values:
                temp_c = values[0x42] / 16.0 - 273.15
                print(f"T: {temp_c:5.2f}", end="   ")
            if 0x44 in values:
                rh = values[0x44] / 100.0
                print(f"RH: {rh:5.2f}", end="   ")

            print()  # newline for next reading

if __name__ == "__main__":
    main()
