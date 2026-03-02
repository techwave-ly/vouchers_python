import os
from vouchers import VouchersClient, APIError

def main():
    # 1. Initialize the client
    # Best practice is to load these from your environment variables
    API_KEY_ID = os.environ.get("API_KEY_ID", "your_api_key_id_here")
    API_SECRET = os.environ.get("API_SECRET", "your_api_secret_here")
    BASE_URL = os.environ.get("BASE_URL", "https://localhost:3000") # Replace with production URL

    client = VouchersClient(api_key_id=API_KEY_ID, api_secret=API_SECRET, base_url=BASE_URL, verify_ssl=False)

    try:
        # 2. Switch to 'test' mode intentionally so vouchers won't deduct real balances
        print("Switching to TEST mode...")
        mode_response = client.switch_mode("test")
        print(mode_response)

        # 3. Issue a single voucher for 150 LYD
        print("\nIssuing a voucher...")
        issue_response = client.issue_voucher(amount=150.0)
        print(issue_response)

        # Assuming issuance succeeded, capture the voucher ID
        voucher_id = issue_response["voucher"]["id"]
        
        # 4. Check voucher status
        print(f"\nChecking status of {voucher_id}...")
        status_response = client.get_voucher_status(voucher_id)
        print(status_response)

        # 5. Void the voucher we just created
        print(f"\nVoiding voucher {voucher_id}...")
        void_response = client.void_voucher(voucher_id)
        print(void_response)

        # 6. Check status again to see it is now void
        print(f"\nChecking status of {voucher_id} after void...")
        status_response = client.get_voucher_status(voucher_id)
        print(status_response)

        # 7. Bulk Issue 5 vouchers at once for 50 LYD
        print("\nBulk-issuing 5 vouchers...")
        bulk_response = client.bulk_issue_vouchers(amount=50.0, count=5)
        print(f"Issued {len(bulk_response.get('vouchers', []))} vouchers.")
        for v in bulk_response.get("vouchers", []):
             print(f"- [IsTest: {v.get('isTest')}] Code: {v['code']} | ID: {v['id']}")

    except APIError as e:
        print(f"API Error ({e.status_code}): {e.message}")
        print("Details:", e.response_body)

if __name__ == "__main__":
    main()
