import argparse
import hashlib
import time
import json
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def calculate_signature(secret: str, current_time: int) -> str:
    """
    Both Protrack and IOPGPS use the exact same signature algorithm:
    md5(md5(secret) + time)
    """
    md5_secret = hashlib.md5(secret.encode('utf-8')).hexdigest()
    combined_string = md5_secret + str(current_time)
    return hashlib.md5(combined_string.encode('utf-8')).hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Generate time and signature auth parameters for Postman.")
    parser.add_argument("--provider", choices=["iopgps", "protrack"], required=True, help="Provider to generate for")
    args = parser.parse_args()

    if args.provider == "iopgps":
        account = os.getenv("IOPGPS_APPID")
        secret = os.getenv("IOPGPS_APPKEY")
        identifier_field = "appid"
        if not account or not secret:
            print("Error: Missing IOPGPS_APPID or IOPGPS_APPKEY in .env")
            return
    else:  # protrack
        account = os.getenv("PROTRACK_ACCOUNT")
        secret = os.getenv("PROTRACK_PASSWORD")
        identifier_field = "account"
        if not account or not secret:
            print("Error: Missing PROTRACK_ACCOUNT or PROTRACK_PASSWORD in .env")
            return

    current_time = int(time.time())
    signature = calculate_signature(secret, current_time)
    
    # Generate a 24-hour window for mileage queries
    start_time = current_time - 86400
    end_time = current_time

    # For Postman body
    postman_body = {
        identifier_field: account,
        "time": current_time,
        "signature": signature
    }

    print("\n" + "="*60)
    print(f" {args.provider.upper()} - AUTHENTICATION PARAMETERS GENERATOR")
    print("="*60)
    print(f"Algorithm Used: md5(md5(secret) + time)\n")
    print("Use the following JSON body in Postman for Login (/api/auth):")
    print("-" * 60)
    print(json.dumps(postman_body, indent=4))
    print("-" * 60)
    
    print("\nHelpful UNIX Timestamps for Mileage/Playback Queries:")
    print(f"startTime (24 hours ago): {start_time}")
    print(f"endTime   (Right now):    {end_time}")
    print("-" * 60)
    
    if args.provider == "iopgps":
        print("\nLogin Endpoint: POST https://open.iopgps.com/api/auth")
    else:
        print(f"\nLogin Endpoint: GET https://api.protrack365.com/api/authorization?time={current_time}&account={account}&signature={signature}")

if __name__ == "__main__":
    main()
