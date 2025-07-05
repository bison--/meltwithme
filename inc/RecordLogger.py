import csv
import os
import datetime

class RecordLogger:
    """
    CSV logger that writes to a new file each day, named by date.

    Usage:
        logger = DailyCSVLogger(
            base_dir='data',
            prefix='record_',
            date_format='%Y-%m-%d',
            ext='.csv',
            header_fields=['timestamp', 'co2', 'temp']
        )
        logger.write_row([measure_date, current_co2, current_temp])
        logger.close()
    """
    def __init__(self, base_dir='data', prefix='record_', date_format='%Y-%m-%d', ext='.csv', header_fields=None):
        self.base_dir = base_dir
        self.prefix = prefix
        self.date_format = date_format
        self.ext = ext
        self.header_fields = header_fields or []

        # Ensure output directory exists
        os.makedirs(self.base_dir, exist_ok=True)

        self.current_date = None
        self.csv_file = None
        self.csv_writer = None

        # Initialize first file
        self._rotate_if_needed()

    def _get_date_str(self):
        return datetime.datetime.now().strftime(self.date_format)

    def _get_filepath(self, date_str):
        return os.path.join(self.base_dir, f"{self.prefix}{date_str}{self.ext}")

    def _rotate_if_needed(self):
        today = self._get_date_str()
        if today == self.current_date:
            return

        # Close previous file if open
        if self.csv_file:
            try:
                self.csv_file.close()
            except Exception:
                pass

        # Open new file for today
        filepath = self._get_filepath(today)
        is_new = not os.path.exists(filepath)
        self.csv_file = open(filepath, 'a', newline='')
        self.csv_writer = csv.writer(self.csv_file)

        # Write header if file is newly created
        if self.header_fields and is_new:
            self.csv_writer.writerow(self.header_fields)
            self.csv_file.flush()

        self.current_date = today

    def write_row(self, row):
        self._rotate_if_needed()
        self.csv_writer.writerow(row)
        self.csv_file.flush()

    def close(self):
        if not self.csv_file:
            return
        try:
            self.csv_file.close()
        except Exception:
            pass
        finally:
            self.csv_file = None
            self.csv_writer = None
            self.current_date = None
