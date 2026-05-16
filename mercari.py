import requests
import jwt
import base64
import uuid
import time
from cryptography.hazmat.primitives.asymmetric import ec

# generate a key pair once and reuse it across requests (used by make_valid_header)
PRIVATE_KEY = ec.generate_private_key(ec.SECP256R1())
PUBLIC_KEY = PRIVATE_KEY.public_key()


def make_valid_header(http_method: str, url: str) -> dict:
    mercari_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ja',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Content-Type': 'application/json',
        'X-Platform': 'web',
        'X-Country-Code': 'US',
        'Origin': 'https://jp.mercari.com',
        'Connection': 'keep-alive',
        'Referer': 'https://jp.mercari.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'Idempotency-Key': '"11432578277613167492"',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'TE': 'trailers',
    }

    # thank you https://www.jwt.io/
    def generate_dpop_proof(method: str, url: str) -> str:
        def int_to_base64url(n: int, length: int = 32) -> str:
            # all decode does is convert this from bytes to a utf-8 string
            # even though this is base64url the python function leaves in the padding '=' chars so remove them
            # length = 32 bytes because we're using, well, a 256-bit key
            return base64.urlsafe_b64encode(n.to_bytes(length, byteorder="big")).decode().rstrip("=")

        headers = {
            "typ": "dpop+jwt",
            "alg": "ES256",
            "jwk": {
                "crv": "P-256",
                "kty": "EC",
                "x": int_to_base64url(PUBLIC_KEY.public_numbers().x),
                "y": int_to_base64url(PUBLIC_KEY.public_numbers().y),
            },
        }
        # the only thing that actually needs to change between requests is the payload
        payload = {
            "jti": str(uuid.uuid4()),  # Unique ID per request
            "htm": method,  # HTTP method
            "htu": url,  # Target URL
            "iat": int(time.time()),  # Current timestamp
        }
        # this function does the "signature" part of the header.payload.signature format
        return jwt.encode(
            payload,
            PRIVATE_KEY,
            algorithm="ES256",
            headers=headers
        )

    ret = dict(mercari_headers)
    ret.update({'DPoP': generate_dpop_proof(http_method, url)})
    return ret


# get the ids of the 120 (or potentially less) results that would appear doing a normal search for the given term.
# always sorts by newest, because that's the whole point.
def get_ids_from_search(search: str) -> list[str] | None:
    json_data = {
        'userId': '',
        'config': {
            'responseToggles': [
                'QUERY_SUGGESTION_WEB_1',
            ],
        },
        'pageSize': 120,
        'pageToken': '',
        'searchSessionId': 'c83bbb3d087c6baa398a460d06a0cefc',
        'source': 'BaseSerp',
        'indexRouting': 'INDEX_ROUTING_UNSPECIFIED',
        'thumbnailTypes': [],
        'searchCondition': {
            'keyword': search,
            'excludeKeyword': '',
            'sort': 'SORT_CREATED_TIME',
            'order': 'ORDER_DESC',
            'status': [],
            'sizeId': [],
            'categoryId': [],
            'brandId': [],
            'sellerId': [],
            'priceMin': 0,
            'priceMax': 0,
            'itemConditionId': [],
            'shippingPayerId': [],
            'shippingFromArea': [],
            'shippingMethod': [],
            'colorId': [],
            'hasCoupon': False,
            'attributes': [],
            'itemTypes': [],
            'skuIds': [],
            'shopIds': [],
            'excludeShippingMethodIds': [],
        },
        'serviceFrom': 'suruga',
        'withItemBrand': True,
        'withItemSize': False,
        'withItemPromotions': True,
        'withItemSizes': True,
        'withShopname': False,
        'useDynamicAttribute': True,
        'withSuggestedItems': True,
        'withOfferPricePromotion': True,
        'withProductSuggest': True,
        'withParentProducts': False,
        'withProductArticles': True,
        'withSearchConditionId': False,
        'withAuction': True,
        'laplaceDeviceUuid': 'fa3a3ca3-e696-4d01-a2f5-49eb502e1c38',
    }
    url = "https://api.mercari.jp/v2/entities:search"
    response = requests.post(url, json=json_data, headers=make_valid_header("POST", url))

    if not response.ok:
        return None

    json = response.json()
    ret = []
    for item in json['items']:
        ret.append(item['id'])
    return ret
