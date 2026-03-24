"""
Module to generate Unix timestamps from user-specified dates.
Supports multiple date formats and provides both command-line and function interfaces.
Includes helper functions for Protrack API integration.
"""

from datetime import datetime
from typing import Optional, Tuple
import sys


def date_to_timestamp(date_input: str, date_format: Optional[str] = None) -> int:
    """
    Convert a date string to a Unix timestamp (seconds since epoch).
    
    Args:
        date_input: Date string in various formats (YYYY-MM-DD, YYYY-MM-DD HH:MM:SS, etc.)
        date_format: Optional format string (e.g., '%Y-%m-%d', '%Y-%m-%d %H:%M:%S')
                     If None, will try common formats automatically.
    
    Returns:
        Unix timestamp as integer (seconds since January 1, 1970 UTC)
    
    Raises:
        ValueError: If the date string cannot be parsed with any supported format
    """
    # List of common date formats to try if no format is specified
    common_formats: list[str] = [
        '%Y-%m-%d %H:%M:%S',      # 2024-01-15 14:30:00
        '%Y-%m-%d %H:%M',         # 2024-01-15 14:30
        '%Y-%m-%d',               # 2024-01-15
        '%d/%m/%Y %H:%M:%S',      # 15/01/2024 14:30:00
        '%d/%m/%Y %H:%M',         # 15/01/2024 14:30
        '%d/%m/%Y',               # 15/01/2024
        '%m/%d/%Y %H:%M:%S',      # 01/15/2024 14:30:00
        '%m/%d/%Y %H:%M',         # 01/15/2024 14:30
        '%m/%d/%Y',               # 01/15/2024
        '%Y%m%d %H%M%S',          # 20240115 143000
        '%Y%m%d',                 # 20240115
    ]
    
    # If a specific format is provided, use only that format
    formats_to_try: list[str] = [date_format] if date_format else common_formats
    
    # Try to parse the date with each format
    for fmt in formats_to_try:
        try:
            # Parse the date string into a datetime object
            dt: datetime = datetime.strptime(date_input, fmt)
            # Convert to Unix timestamp (seconds since epoch)
            timestamp: int = int(dt.timestamp())
            return timestamp
        except ValueError:
            # Continue to next format if this one doesn't work
            continue
    
    # If all formats failed, raise an error
    raise ValueError(
        f"Unable to parse date '{date_input}'. "
        f"Please use a format like 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'"
    )


def timestamp_to_date(timestamp: int) -> str:
    """
    Convert a Unix timestamp back to a readable date string.
    
    Args:
        timestamp: Unix timestamp (seconds since epoch)
    
    Returns:
        Formatted date string in ISO format
    """
    dt: datetime = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def adjust_timestamp_for_protrack(timestamp: int, round_up: bool = False) -> int:
    """
    Adjust a timestamp to comply with Protrack API requirements.
    Protrack API requires that minutes must be either 0 or 30.
    
    Args:
        timestamp: Unix timestamp to adjust
        round_up: If True, round up to next valid minute (0 or 30).
                  If False, round down to previous valid minute.
    
    Returns:
        Adjusted Unix timestamp with minutes set to 0 or 30
    """
    # Convert timestamp to datetime object
    dt: datetime = datetime.fromtimestamp(timestamp)
    
    # Get current minute value
    current_minute: int = dt.minute
    
    # Determine target minute based on rounding direction
    if round_up:
        # Round up: find the smallest valid time >= current time
        if current_minute == 0:
            # Already valid, keep it
            target_minute: int = 0
        elif current_minute <= 30:
            # Round up to 30
            target_minute: int = 30
        else:
            # Round up to 0 of next hour
            dt = dt.replace(hour=dt.hour + 1, minute=0, second=0, microsecond=0)
            adjusted_timestamp: int = int(dt.timestamp())
            return adjusted_timestamp
    else:
        # Round down: find the largest valid time <= current time
        if current_minute < 30:
            # Round down to 0
            target_minute: int = 0
        else:
            # Round down to 30
            target_minute: int = 30
    
    # Adjust the datetime to have the target minute, and set seconds/microseconds to 0
    adjusted_dt: datetime = dt.replace(minute=target_minute, second=0, microsecond=0)
    adjusted_timestamp: int = int(adjusted_dt.timestamp())
    
    return adjusted_timestamp


def generate_protrack_time_range(
    start_date: str, 
    end_date: Optional[str] = None,
    start_date_format: Optional[str] = None,
    end_date_format: Optional[str] = None
) -> Tuple[int, int]:
    """
    Generate begintime and endtime timestamps for Protrack API calls.
    Automatically adjusts timestamps to comply with Protrack API requirements:
    minutes must be either 0 or 30.
    
    Args:
        start_date: Start date string (will be used for begintime)
        end_date: End date string (will be used for endtime). 
                  If None, defaults to end of start_date (23:30:00)
        start_date_format: Optional format string for start_date
        end_date_format: Optional format string for end_date
    
    Returns:
        Tuple of (begintime, endtime) as Unix timestamps with minutes = 0 or 30
    
    Raises:
        ValueError: If dates cannot be parsed
    """
    # Convert start date to timestamp (begintime)
    begintime: int = date_to_timestamp(start_date, start_date_format)
    # Adjust to comply with Protrack API (round down for start time)
    begintime = adjust_timestamp_for_protrack(begintime, round_up=False)
    
    # If end_date is provided, use it; otherwise default to end of start_date
    if end_date:
        endtime: int = date_to_timestamp(end_date, end_date_format)
        # Adjust to comply with Protrack API (round up for end time to include full range)
        endtime = adjust_timestamp_for_protrack(endtime, round_up=True)
    else:
        # Default to end of the start_date (23:30:00, the latest valid time)
        start_dt: datetime = datetime.fromtimestamp(begintime)
        # Set to end of day with valid minute (23:30:00)
        end_dt: datetime = start_dt.replace(hour=23, minute=30, second=0, microsecond=0)
        endtime: int = int(end_dt.timestamp())
    
    # Validate that endtime is after begintime
    if endtime < begintime:
        raise ValueError(
            f"End time ({timestamp_to_date(endtime)}) must be after "
            f"start time ({timestamp_to_date(begintime)})"
        )
    
    return (begintime, endtime)


def verify_protrack_timestamp(timestamp: int) -> bool:
    """
    Verify that a timestamp complies with Protrack API requirements.
    Protrack API requires minutes to be either 0 or 30.
    
    Args:
        timestamp: Unix timestamp to verify
    
    Returns:
        True if timestamp is valid for Protrack API, False otherwise
    """
    dt: datetime = datetime.fromtimestamp(timestamp)
    minute: int = dt.minute
    second: int = dt.second
    # Minutes must be 0 or 30, and seconds should be 0
    return minute in [0, 30] and second == 0


def format_protrack_mileage_url(
    access_token: str,
    imeis: str,
    begintime: int,
    endtime: int,
    verify_timestamps: bool = True
) -> str:
    """
    Format a Protrack API mileage endpoint URL with timestamps.
    
    Args:
        access_token: Protrack API access token
        imeis: Device IMEI number
        begintime: Start time as Unix timestamp
        endtime: End time as Unix timestamp
        verify_timestamps: If True, verify timestamps comply with Protrack API requirements
    
    Returns:
        Complete API URL string
    
    Raises:
        ValueError: If verify_timestamps is True and timestamps don't comply
    """
    # Verify timestamps if requested
    if verify_timestamps:
        if not verify_protrack_timestamp(begintime):
            raise ValueError(
                f"begintime {begintime} ({timestamp_to_date(begintime)}) "
                f"does not comply with Protrack API requirements (minutes must be 0 or 30)"
            )
        if not verify_protrack_timestamp(endtime):
            raise ValueError(
                f"endtime {endtime} ({timestamp_to_date(endtime)}) "
                f"does not comply with Protrack API requirements (minutes must be 0 or 30)"
            )
    
    base_url: str = "https://api.protrack365.com/api/device/mileage"
    url: str = (
        f"{base_url}?"
        f"access_token={access_token}&"
        f"imeis={imeis}&"
        f"begintime={begintime}&"
        f"endtime={endtime}"
    )
    return url


def main() -> None:
    """
    Main function to handle command-line usage.
    Prompts user for dates and displays the corresponding timestamps for Protrack API.
    """
    print("=" * 60)
    print("Protrack API Timestamp Generator")
    print("=" * 60)
    print("\nNote: Protrack API requires minutes to be 0 or 30.")
    print("Timestamps will be automatically adjusted to comply.")
    print("\nSupported date formats:")
    print("  - YYYY-MM-DD (e.g., 2024-01-15)")
    print("  - YYYY-MM-DD HH:MM:SS (e.g., 2024-01-15 14:30:00)")
    print("  - DD/MM/YYYY (e.g., 15/01/2024)")
    print("  - MM/DD/YYYY (e.g., 01/15/2024)")
    print("  - And other common formats")
    print("\n" + "-" * 60)
    
    # Get start date input from user
    start_date: str = input("\nEnter start date (begintime): ").strip()
    
    if not start_date:
        print("Error: No start date provided.")
        sys.exit(1)
    
    # Get end date input from user (optional)
    end_date: Optional[str] = input("Enter end date (endtime) [optional, press Enter for end of start date]: ").strip()
    if not end_date:
        end_date = None
    
    try:
        # Generate timestamps for Protrack API
        begintime, endtime = generate_protrack_time_range(start_date, end_date)
        
        # Display results
        print("\n" + "=" * 60)
        print("Results:")
        print("=" * 60)
        print(f"Start date:     {start_date}")
        if end_date:
            print(f"End date:       {end_date}")
        else:
            print(f"End date:       (defaulted to end of start date)")
        print(f"\nbegintime:      {begintime}")
        print(f"endtime:        {endtime}")
        print(f"\nReadable start: {timestamp_to_date(begintime)}")
        print(f"Readable end:   {timestamp_to_date(endtime)}")
        print("\n" + "-" * 60)
        print("Protrack API URL format:")
        print("-" * 60)
        print("https://api.protrack365.com/api/device/mileage?")
        print(f"  access_token=YOUR_TOKEN&")
        print(f"  imeis=YOUR_IMEI&")
        print(f"  begintime={begintime}&")
        print(f"  endtime={endtime}")
        print("=" * 60)
        
    except ValueError as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

