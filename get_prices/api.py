import logging

logger = logging.getLogger(__name__)

API_URL = "https://web.np.playstation.com/api/graphql/v1/op"

SEARCH_REGION = "en-us"

SEARCH_HASH = (
    "4df6284f982e57bec70f23c77e2c219dc792eb19af7fb3d3a81767aa3f1958aa"
)

CONCEPT_BY_PRODUCT_HASH = (
    "0a4c9f3693b3604df1c8341fdc3e481f42eeecf961a996baaa65e65a657a6433"
)

CONCEPT_BY_ID_HASH = (
    "cc90404ac049d935afbd9968aef523da2b6723abfb9d586e5f77ebf7c5289006"
)

MAIN_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "apollographql-client-name": "@sie-ppr-web-store/app",
    "apollographql-client-version": "0.113.0",
    "x-psn-app-ver": "@sie-ppr-web-store/app/0.113.0-",
}
