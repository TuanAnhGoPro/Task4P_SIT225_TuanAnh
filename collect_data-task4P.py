

import serial
import pandas as pd
from datetime import datetime, timedelta
import time

# ---------------- CONFIG ----------------
PORT = 'COM3'              # <-- change this to your port
BAUD = 9600
DURATION_HOURS = 4
OUTPUT_FILE = 'raw_data.csv'
RECONNECT_DELAY = 5        # seconds to wait before retrying if USB drops
SAVE_EVERY_N_ROWS = 5      # write to disk periodically so no data is lost on crash
# -----------------------------------------

def connect_serial():
    """Try to open the serial port, retrying if it fails."""
    while True:
        try:
            s = serial.Serial(PORT, BAUD, timeout=1)
            time.sleep(2)  # allow connection to stabilize
            print(f"[{datetime.now().isoformat()}] Connected to {PORT}")
            return s
        except serial.SerialException as e:
            print(f"[{datetime.now().isoformat()}] Could not open {PORT}: {e}")
            print(f"Retrying in {RECONNECT_DELAY} seconds...")
            time.sleep(RECONNECT_DELAY)


def main():
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=DURATION_HOURS)

    print("=" * 50)
    print(f"Data collection started: {start_time.isoformat()}")
    print(f"Scheduled to stop at:   {end_time.isoformat()}")
    print(f"Duration: {DURATION_HOURS} hour(s)")
    print("=" * 50)

    ser = connect_serial()
    data = []
    row_count = 0
    error_count = 0

    try:
        while datetime.now() < end_time:
            try:
                line = ser.readline().decode(errors='ignore').strip()
            except (serial.SerialException, OSError):
                # USB likely disconnected - try to reconnect
                print(f"[{datetime.now().isoformat()}] Serial connection lost. Reconnecting...")
                try:
                    ser.close()
                except Exception:
                    pass
                ser = connect_serial()
                continue

            if not line:
                continue

            parts = line.split(",")
            if len(parts) != 3:
                error_count += 1
                continue

            try:
                row = {
                    'timestamp': datetime.now().isoformat(),
                    'temperature': float(parts[0]),
                    'humidity': float(parts[1]),
                    'motion': int(parts[2])
                }
                data.append(row)
                row_count += 1

                # Print every reading immediately so you can see it live
                print(f"[{row['timestamp']}] Temp: {row['temperature']}C | "
                      f"Humidity: {row['humidity']}% | "
                      f"Motion: {'Yes' if row['motion'] == 1 else 'No'}")

                if row_count % SAVE_EVERY_N_ROWS == 0:
                    pd.DataFrame(data).to_csv(OUTPUT_FILE, index=False)
                    print(f"[{datetime.now().isoformat()}] Saved {row_count} rows so far...")

            except ValueError:
                # e.g. "nan" or malformed reading from DHT22
                error_count += 1
                continue

    except KeyboardInterrupt:
        print(f"\n[{datetime.now().isoformat()}] Manually stopped by user (Ctrl+C).")

    finally:
        df = pd.DataFrame(data)
        df.to_csv(OUTPUT_FILE, index=False)
        actual_end_time = datetime.now()

        print("=" * 50)
        print("COLLECTION SUMMARY")
        print(f"Start time:        {start_time.isoformat()}")
        print(f"End time:          {actual_end_time.isoformat()}")
        print(f"Total duration:    {actual_end_time - start_time}")
        print(f"Total rows saved:  {len(df)}")
        print(f"Skipped/error rows:{error_count}")
        print(f"Output file:       {OUTPUT_FILE}")
        print("=" * 50)

        try:
            ser.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()