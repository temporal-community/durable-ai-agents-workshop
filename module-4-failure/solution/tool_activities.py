from urllib.parse import quote

import httpx
from temporalio import activity
from temporalio.exceptions import ApplicationError


@activity.defn
async def get_ip_address() -> str:
    """Get the public IP address of the machine running this agent."""
    async with httpx.AsyncClient() as client:
        response = await client.get("https://icanhazip.com", timeout=5.0)
        response.raise_for_status()
        return response.text.strip()


@activity.defn
async def get_location_info(ipaddress: str) -> str:
    """Get the city, region, country, latitude and longitude for an IP address.

    Args:
        ipaddress: An IP address.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://ip-api.com/json/{ipaddress}", timeout=5.0)
        response.raise_for_status()
        return response.text


@activity.defn
async def get_coordinates(city: str) -> str:
    """Get the latitude and longitude for a city name.

    Args:
        city: The city name to look up.
    """
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={quote(city)}&count=1"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=5.0)
        response.raise_for_status()
        return response.text


@activity.defn
async def get_weather(latitude: float, longitude: float) -> str:
    """Get the current temperature, weather code and wind speed for a location.

    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.
    """
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        "&current=temperature_2m,weather_code,wind_speed_10m"
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=5.0)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as err:
            # A 4xx will fail the same way on every attempt, so stop Temporal retrying it.
            if response.status_code < 500:
                raise ApplicationError(
                    f"Weather API rejected the request: {response.status_code}",
                    type="WeatherClientError",
                    non_retryable=True,
                ) from err
            raise
        return response.text
