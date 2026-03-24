"""
Module to fetch and store vehicle mileage data from Protrack API.
Ensures accurate timestamp generation and proper data storage.
"""

import requests
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from generate_timestamp import (
    generate_protrack_time_range,
    format_protrack_mileage_url,
    timestamp_to_date,
    verify_protrack_timestamp
)


class MileageData:
    """
    Data class to represent mileage information for a vehicle.
    """
    def __init__(
        self,
        imei: str,
        mileage: float,
        begintime: int,
        endtime: int,
        fetched_at: Optional[datetime] = None
    ):
        """
        Initialize mileage data record.
        
        Args:
            imei: Device IMEI number
            mileage: Mileage value in kilometers
            begintime: Start timestamp for the mileage period
            endtime: End timestamp for the mileage period
            fetched_at: Timestamp when data was fetched (defaults to now)
        """
        self.imei: str = imei
        self.mileage: float = mileage
        self.begintime: int = begintime
        self.endtime: int = endtime
        self.fetched_at: datetime = fetched_at if fetched_at else datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert mileage data to dictionary format for storage.
        
        Returns:
            Dictionary representation of the mileage data
        """
        return {
            "imei": self.imei,
            "mileage": self.mileage,
            "begintime": self.begintime,
            "endtime": self.endtime,
            "begin_date": timestamp_to_date(self.begintime),
            "end_date": timestamp_to_date(self.endtime),
            "fetched_at": self.fetched_at.isoformat()
        }
    
    def __repr__(self) -> str:
        """String representation of the mileage data."""
        return (
            f"MileageData(imei={self.imei}, mileage={self.mileage}, "
            f"period={timestamp_to_date(self.begintime)} to {timestamp_to_date(self.endtime)})"
        )


def fetch_vehicle_mileage(
    access_token: str,
    imeis: str,
    start_date: str,
    end_date: Optional[str] = None,
    start_date_format: Optional[str] = None,
    end_date_format: Optional[str] = None,
    verbose: bool = True
) -> List[MileageData]:
    """
    Fetch vehicle mileage data from Protrack API with accurate timestamps.
    
    Args:
        access_token: Protrack API access token
        imeis: Device IMEI number (single IMEI as string)
        start_date: Start date string (will be converted to begintime)
        end_date: End date string (will be converted to endtime).
                  If None, defaults to end of start_date
        start_date_format: Optional format string for start_date
        end_date_format: Optional format string for end_date
        verbose: If True, print detailed information about the request
    
    Returns:
        List of MileageData objects containing the fetched mileage information
    
    Raises:
        ValueError: If dates cannot be parsed or timestamps are invalid
        requests.RequestException: If API request fails
        RuntimeError: If API returns an error code
    """
    # Generate accurate timestamps that comply with Protrack API requirements
    begintime, endtime = generate_protrack_time_range(
        start_date,
        end_date,
        start_date_format,
        end_date_format
    )
    
    # Validate timestamps are valid
    if begintime >= endtime:
        raise ValueError(
            f"Invalid time range: begintime ({begintime}) must be before endtime ({endtime})"
        )
    
    # Verify timestamps comply with Protrack API requirements (double-check)
    if not verify_protrack_timestamp(begintime):
        raise ValueError(
            f"begintime {begintime} ({timestamp_to_date(begintime)}) "
            f"does not comply with Protrack API requirements (minutes must be 0 or 30). "
            f"This should not happen - please report this issue."
        )
    if not verify_protrack_timestamp(endtime):
        raise ValueError(
            f"endtime {endtime} ({timestamp_to_date(endtime)}) "
            f"does not comply with Protrack API requirements (minutes must be 0 or 30). "
            f"This should not happen - please report this issue."
        )
    
    # Format the API URL with accurate timestamps
    url: str = format_protrack_mileage_url(access_token, imeis, begintime, endtime)
    
    if verbose:
        print("=" * 70)
        print("Fetching Vehicle Mileage Data")
        print("=" * 70)
        print(f"IMEI:           {imeis}")
        print(f"Start Date:     {start_date}")
        if end_date:
            print(f"End Date:       {end_date}")
        else:
            print(f"End Date:       (defaulted to end of start date)")
        print(f"begintime:      {begintime} ({timestamp_to_date(begintime)})")
        print(f"endtime:        {endtime} ({timestamp_to_date(endtime)})")
        print(f"\nAPI URL: {url}")
        print("-" * 70)
    
    # Send GET request to Protrack API
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Raises an error for HTTP error codes
        data: Dict[str, Any] = response.json()
        
        if verbose:
            print(f"Response Status: {response.status_code}")
            print(f"Response Data: {json.dumps(data, indent=2)}")
            print("-" * 70)
        
        # Check API response code
        api_code: int = data.get("code", -1)
        if api_code != 0:
            error_message: str = data.get("message", "Unknown error")
            raise RuntimeError(
                f"Protrack API error (code {api_code}): {error_message}"
            )
        
        # Extract mileage records from response
        records: List[Dict[str, Any]] = data.get("record", [])
        if not records:
            if verbose:
                print("Warning: No mileage records found in response")
            return []
        
        # Convert API response to MileageData objects
        mileage_data_list: List[MileageData] = []
        for record in records:
            record_imei: str = str(record.get("imei", ""))
            record_mileage: float = float(record.get("mileage", 0.0))
            
            mileage_data: MileageData = MileageData(
                imei=record_imei,
                mileage=record_mileage,
                begintime=begintime,
                endtime=endtime
            )
            mileage_data_list.append(mileage_data)
            
            if verbose:
                print(f"✓ Fetched: {mileage_data}")
        
        if verbose:
            print("=" * 70)
            print(f"Successfully fetched {len(mileage_data_list)} mileage record(s)")
            print("=" * 70)
        
        return mileage_data_list
        
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Failed to fetch mileage data from Protrack API: {str(e)}"
        )


def fetch_multiple_vehicles_mileage(
    access_token: str,
    imeis_list: List[str],
    start_date: str,
    end_date: Optional[str] = None,
    start_date_format: Optional[str] = None,
    end_date_format: Optional[str] = None,
    verbose: bool = True
) -> Dict[str, List[MileageData]]:
    """
    Fetch mileage data for multiple vehicles.
    
    Args:
        access_token: Protrack API access token
        imeis_list: List of IMEI numbers to fetch data for
        start_date: Start date string (will be converted to begintime)
        end_date: End date string (will be converted to endtime)
        start_date_format: Optional format string for start_date
        end_date_format: Optional format string for end_date
        verbose: If True, print detailed information
    
    Returns:
        Dictionary mapping IMEI to list of MileageData objects
    """
    results: Dict[str, List[MileageData]] = {}
    
    for imei in imeis_list:
        try:
            mileage_data = fetch_vehicle_mileage(
                access_token=access_token,
                imeis=imei,
                start_date=start_date,
                end_date=end_date,
                start_date_format=start_date_format,
                end_date_format=end_date_format,
                verbose=verbose
            )
            results[imei] = mileage_data
        except Exception as e:
            if verbose:
                print(f"Error fetching data for IMEI {imei}: {str(e)}")
            results[imei] = []
    
    return results


def save_mileage_data_to_json(
    mileage_data_list: List[MileageData],
    filepath: str,
    indent: int = 2
) -> None:
    """
    Save mileage data to a JSON file.
    
    Args:
        mileage_data_list: List of MileageData objects to save
        filepath: Path to the JSON file to save to
        indent: JSON indentation level (default: 2)
    """
    # Convert all MileageData objects to dictionaries
    data_to_save: List[Dict[str, Any]] = [
        mileage_data.to_dict() for mileage_data in mileage_data_list
    ]
    
    # Write to JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, indent=indent, ensure_ascii=False)
    
    print(f"✓ Saved {len(mileage_data_list)} mileage record(s) to {filepath}")


def load_mileage_data_from_json(filepath: str) -> List[MileageData]:
    """
    Load mileage data from a JSON file.
    
    Args:
        filepath: Path to the JSON file to load from
    
    Returns:
        List of MileageData objects
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data: List[Dict[str, Any]] = json.load(f)
    
    mileage_data_list: List[MileageData] = []
    for record in data:
        mileage_data = MileageData(
            imei=record["imei"],
            mileage=record["mileage"],
            begintime=record["begintime"],
            endtime=record["endtime"],
            fetched_at=datetime.fromisoformat(record["fetched_at"])
        )
        mileage_data_list.append(mileage_data)
    
    return mileage_data_list


if __name__ == "__main__":
    """
    Example usage of the mileage fetching functionality.
    """
    # Example: Fetch mileage data for a vehicle
    # Note: Replace with actual access token and IMEI
    # access_token = "YOUR_ACCESS_TOKEN"
    # imei = "355710090499992"
    # 
    # mileage_data = fetch_vehicle_mileage(
    #     access_token=access_token,
    #     imeis=imei,
    #     start_date="2024-01-15",
    #     end_date="2024-01-16"
    # )
    # 
    # # Save to file
    # save_mileage_data_to_json(mileage_data, "mileage_data.json")
    
    print("Mileage fetching module loaded.")
    print("Import this module and use fetch_vehicle_mileage() to fetch data.")

