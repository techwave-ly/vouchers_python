import json
import uuid
import urllib.request
import urllib.error
import ssl
from typing import Dict, Any, Optional

class APIError(Exception):
    def __init__(self, message: str, status_code: int, response_body: Any):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body

class VouchersClient:
    """
    A Python client SDK for the Wave Commerce Partner Vouchers API.
    Designed to work immediately out-of-the-box using built-in Python libraries.
    """

    def __init__(self, api_key_id: str, api_secret: str, base_url: str, verify_ssl: bool = True):
        """
        Initialize the Python client for B2B API integrations.
        
        :param api_key_id: X-Api-Key-Id provided by Admin dashboard
        :param api_secret: X-Api-Secret provided by Admin dashboard
        :param base_url: URL to the target environment (e.g. 'https://api.wavecommerce.ly')
        :param verify_ssl: Set to False only for local development with self-signed certificates
        """
        self.api_key_id = api_key_id
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')
        self.verify_ssl = verify_ssl

    def _request(self, method: str, endpoint: str, payload: Optional[Dict[str, Any]] = None, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Internal method to make requests and securely attach the credentials.
        """
        url = f"{self.base_url}{endpoint}"
        idem_key = idempotency_key or str(uuid.uuid4())

        headers = {
            "X-Api-Key-Id": self.api_key_id,
            "X-Api-Secret": self.api_secret,
            "X-Idempotency-Key": idem_key,
            "Accept": "application/json"
        }

        data = None
        if payload is not None:
            data = json.dumps(payload).encode('utf-8')
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        ctx = None
        if not self.verify_ssl:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        try:
            with urllib.request.urlopen(req, context=ctx) as response:
                response_str = response.read().decode('utf-8')
                return json.loads(response_str)

        except urllib.error.HTTPError as e:
            error_str = e.read().decode('utf-8')
            try:
                error_body = json.loads(error_str)
                error_msg = error_body.get('error', e.reason)
            except json.JSONDecodeError:
                error_body = error_str
                error_msg = e.reason

            raise APIError(f"API Request failed: {error_msg}", e.code, error_body)
        
        except urllib.error.URLError as e:
            raise APIError(f"Network error: {str(e.reason)}", 0, None)
        except Exception as e:
            raise APIError(f"Unexpected connection error: {str(e)}", 0, None)

    def issue_voucher(self, amount: float, campaign_id: Optional[str] = None, expires_at: Optional[str] = None, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Issue a single voucher.
        
        :param amount: The voucher value (e.g., 100 for 100 LYD).
        :param campaign_id: (Optional) ID of a specific campaign to tie this voucher to.
        :param expires_at: (Optional) ISO 8601 formatted datetime string (e.g., '2027-12-31T23:59:59Z').
        :param idempotency_key: (Optional) Override the auto-generated idempotency key.
        """
        payload = {
            "amount": amount,
            "currency": "LYD"
        }
        if campaign_id:
            payload["campaignId"] = campaign_id
        if expires_at:
            payload["expiresAt"] = expires_at

        return self._request("POST", "/api/partner/v1/vouchers/issue", payload, idempotency_key)

    def bulk_issue_vouchers(self, amount: float, count: int, campaign_id: Optional[str] = None, expires_at: Optional[str] = None, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Issue multiple vouchers at once (maximum 1000).
        
        :param count: Total number of vouchers to generate instantly. Max 1000.
        """
        payload = {
            "amount": amount,
            "currency": "LYD",
            "count": count
        }
        if campaign_id:
            payload["campaignId"] = campaign_id
        if expires_at:
            payload["expiresAt"] = expires_at

        return self._request("POST", "/api/partner/v1/vouchers/bulk-issue", payload, idempotency_key)

    def void_voucher(self, voucher_id: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Void an existing active voucher. Once voided, it becomes completely unredeemable.
        
        :param voucher_id: UUID of the voucher returned during issuance.
        """
        payload = {
            "voucherId": voucher_id
        }
        return self._request("POST", "/api/partner/v1/vouchers/void", payload, idempotency_key)

    def get_voucher_status(self, voucher_id: str) -> Dict[str, Any]:
        """
        Get the current life-cycle status of a voucher.
        
        :param voucher_id: UUID of the voucher returned during issuance.
        """
        return self._request("GET", f"/api/partner/v1/vouchers/{voucher_id}/status")

    def switch_mode(self, mode: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Switch the behavior mode of your Partner App between 'test' and 'live'.
        Vouchers generated in 'test' mode cannot manipulate real financial ledgers.
        
        :param mode: 'test' or 'live'
        """
        if mode not in ("test", "live"):
            raise ValueError("Mode must be strictly 'test' or 'live'")
        
        payload = {
            "mode": mode
        }
        return self._request("POST", "/api/partner/v1/mode", payload, idempotency_key)
