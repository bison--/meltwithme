#!/usr/bin/env python3

import sys
import fcntl
import csv
import datetime
import os
import time
import config_loader as config
from inc.DataPoster import DataPoster


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

    record_file = "data/record_{}.csv".format(datetime.datetime.now().strftime("%Y-%m-%d"))
    is_new_file = False

    if not os.path.isfile(record_file):
        is_new_file = True

    csv_file = open(record_file, "a", newline="")
    csv_writer = csv.writer(csv_file)

    if is_new_file:
        csv_writer.writerow([
            'timestamp',
            'co2',
            'temp',
        ])
        csv_file.flush()

    data_poster = DataPoster()

    # Open device for read/write in binary, no buffering
    with open(device_path, "a+b", buffering=0) as fp:
        # HID feature-report ioctl code
        HIDIOCSFEATURE_9 = 0xC0094806

        # Prepend report ID (0) to the 8-byte key
        report = bytes([0] + key)
        fcntl.ioctl(fp, HIDIOCSFEATURE_9, report)

        values: dict[int, int] = {}

        last_co2 = -1
        current_co2 = -1
        last_temp = -1
        current_temp = -1

        while True:
            #time.sleep(1)

            measure_date = datetime.datetime.now()

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
            #print(", ".join(parts), end="   ")

            print(measure_date, end="   ")

            # From http://co2meters.com/Documentation/AppNotes/AN146-RAD-0401-serial-communication.pdf
            if 0x50 in values:
                print(f"CO2: {values[0x50]:4d}", end="   ")
                current_co2 = values[0x50]
            if 0x42 in values:
                temp_c = values[0x42] / 16.0 - 273.15
                print(f"T: {temp_c:5.2f}", end="   ")
                current_temp = round(temp_c, 2)
            if 0x44 in values:
                rh = values[0x44] / 100.0
                print(f"RH: {rh:5.2f}", end="   ")


            print()  # newline for next reading

            if current_co2 == -1 or current_temp == -1:
                continue

            if current_co2 == last_co2 and current_temp == last_temp:
                continue

            last_co2 = current_co2
            last_temp = current_temp

            csv_writer.writerow([
                measure_date,
                current_co2,
                current_temp,
            ])
            csv_file.flush()

            data_poster.post({
                'date': measure_date.strftime("%Y-%m-%d %H:%M:%S"),
                'co2': current_co2,
                'temperature': current_temp,
            })



if __name__ == "__main__":
    main()
