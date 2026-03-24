import hashlib
import time
import requests
from typing import Optional, List
from generate_timestamp import generate_protrack_time_range, format_protrack_mileage_url
from fetch_mileage import (
    fetch_vehicle_mileage,
    fetch_multiple_vehicles_mileage,
    save_mileage_data_to_json,
    MileageData
)

def calculate_signature(password, time):
    # Calculate md5(password)
    md5_password = hashlib.md5(password.encode('utf-8')).hexdigest()
    
    # Concatenate md5(password) and time
    combined_string = md5_password + str(time)
    
    # Calculate md5(md5(password) + time)
    signature = hashlib.md5(combined_string.encode('utf-8')).hexdigest()
    
    return signature


# The expected output should match the example in the image: 3844afd2c3bf68f0f3f4aa0a9ee8ee6c

def get_access_token(account: str, password: str) -> str:
    """
    Generate current UNIX time, calculate the signature, make a request
    to the Protrack API, and extract the access token from the response.
    """
    # Get current time as int
    current_time = int(time.time())
    # Calculate the signature
    signature = calculate_signature(password, current_time)
    
    # Construct the request URL
    url = (
        f"https://api.protrack365.com/api/authorization?"
        f"time={current_time}&account={account}&signature={signature}"
    )
    print("Request URL:", url)
    
    # Send GET request
    response = requests.get(url)
    response.raise_for_status()  # Raises an error if the request failed
    data = response.json()
    print("Response JSON:", data)
    
    # Extract access token as per API documentation
    # Success response sample: { 'code': 0, 'record': { 'access_token': '...', 'expires_in': 7200 } }
    if data.get("code") == 0 and "record" in data and "access_token" in data["record"]:
        print(f"Access token: {data['record']['access_token']}")
        return data["record"]["access_token"]
    else:
        print("Failed to retrieve token; full response:", data)
        return None

# Example credentials should be stored in .env file
    # PROTRACK_ACCOUNT=your_account
    # PROTRACK_PASSWORD=your_password
    pass
def get_device_mileage(
    access_token: str,
    imeis: str,
    start_date: str,
    end_date: Optional[str] = None,
    start_date_format: Optional[str] = None,
    end_date_format: Optional[str] = None
) -> dict:
    """
    Get device mileage data from Protrack API using date strings.
    Legacy function - consider using fetch_vehicle_mileage() for better data handling.
    
    Args:
        access_token: Protrack API access token
        imeis: Device IMEI number
        start_date: Start date string (will be converted to begintime)
        end_date: End date string (will be converted to endtime). 
                  If None, defaults to end of start_date
        start_date_format: Optional format string for start_date
        end_date_format: Optional format string for end_date
    
    Returns:
        API response as dictionary
    
    Raises:
        ValueError: If dates cannot be parsed
        requests.RequestException: If API request fails
    """
    # Generate timestamps from date strings
    begintime, endtime = generate_protrack_time_range(
        start_date, 
        end_date, 
        start_date_format, 
        end_date_format
    )
    
    # Format the API URL
    url: str = format_protrack_mileage_url(access_token, imeis, begintime, endtime)
    print(f"Request URL: {url}")
    
    # Send GET request
    response = requests.get(url)
    response.raise_for_status()  # Raises an error if the request failed
    data: dict = response.json()
    print("Response JSON:", data)
    
    return data


def fetch_and_store_vehicle_mileage(
    access_token: str,
    imeis: str,
    start_date: str,
    end_date: Optional[str] = None,
    output_file: Optional[str] = None,
    start_date_format: Optional[str] = None,
    end_date_format: Optional[str] = None
) -> List[MileageData]:
    """
    Fetch vehicle mileage data and optionally save it to a JSON file.
    This is the recommended function for accurate mileage data fetching.
    
    Args:
        access_token: Protrack API access token
        imeis: Device IMEI number
        start_date: Start date string (will be converted to begintime)
        end_date: End date string (will be converted to endtime)
        output_file: Optional path to JSON file to save the data
        start_date_format: Optional format string for start_date
        end_date_format: Optional format string for end_date
    
    Returns:
        List of MileageData objects containing the fetched mileage information
    """
    # Fetch mileage data with accurate timestamps
    mileage_data: List[MileageData] = fetch_vehicle_mileage(
        access_token=access_token,
        imeis=imeis,
        start_date=start_date,
        end_date=end_date,
        start_date_format=start_date_format,
        end_date_format=end_date_format,
        verbose=True
    )
    
    # Save to file if output path is provided
    if output_file and mileage_data:
        save_mileage_data_to_json(mileage_data, output_file)
    
    return mileage_data


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    account = os.getenv("PROTRACK_ACCOUNT")
    password = os.getenv("PROTRACK_PASSWORD")
    
    if not account or not password:
        print("Please set PROTRACK_ACCOUNT and PROTRACK_PASSWORD in your .env file")
        exit(1)
        
    token = get_access_token(account, password)
    print(f"Test token result: {token}")
    
    # Example usage: Fetch and store vehicle mileage data with accurate timestamps
    if token:
        try:
            # Fetch mileage data for a vehicle with accurate timestamp handling
            mileage_data = fetch_and_store_vehicle_mileage(
                access_token=token,
                imeis="355710090792362",
                start_date="2025-11-15",
                end_date="2025-11-16",
                output_file="mileage_data.json"  # Optional: save to file
            )
            
            # Display results
            print("\n" + "=" * 70)
            print("Mileage Data Summary:")
            print("=" * 70)
            for data in mileage_data:
                print(f"IMEI: {data.imei}")
                print(f"Mileage: {data.mileage} km")
                print(f"Period: {data.to_dict()['begin_date']} to {data.to_dict()['end_date']}")
                print("-" * 70)
                
        except Exception as e:
            print(f"Error fetching mileage data: {str(e)}")