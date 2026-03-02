# Commerce Vouchers Python SDK

A lightweight, dependency-free Python client SDK created for Commerce partners. Plugs directly into B2B endpoints for issuing, tracking, and voiding vouchers programmatically.

## Features

- Securely handles credentials with explicit `X-Api-Key-Id` and `X-Api-Secret` headers.
- Built-in idempotency logic guaranteeing atomic financial events.
- Test Mode integrated out of the box so partners can play around in realistic conditions.

## Installation

Because this library requires no package installations, you can simply clone the repository into your project and install it locally or drop `vouchers` straight into your source tree.

```bash
pip install -e .
```

## Quick Start

```python
from vouchers import VouchersClient, APIError

client = VouchersClient(
    api_key_id="your_api_key",
    api_secret="your_api_secret", 
    base_url="https://localhost:3000"
)

try:
    # Safely switch to testing mode
    client.switch_mode("test")

    # Issue a Single Voucher
    res = client.issue_voucher(amount=100.0)
    voucher_id = res["voucher"]["id"]
    code = res["voucher"]["code"]
    
    print(f"Created Test Voucher: {code}")

    # Check the voucher status
    status = client.get_voucher_status(voucher_id)
    print(f"Is test? {status.get('isTest')}")

    # Bulk create up to 1000 vouchers at once!
    bulk_res = client.bulk_issue_vouchers(amount=20.0, count=10)
    print(f"Issued {len(bulk_res['vouchers'])} bulk vouchers")

    # Change mind? Void them!
    client.void_voucher(voucher_id)
    
except APIError as e:
    print(f"API failed ({e.status_code}): {e.message}")
    print(f"Raw body: {e.response_body}")
```

## Testing Note

Remember that any voucher generated while `mode` is `"test"` will carry `isTest=True`. The Commerce ledger will completely block their consumption for tangible financial credit on the user side. This gives you complete peace of mind while developing your tools!
