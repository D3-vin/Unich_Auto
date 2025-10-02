import asyncio
import base64
from typing import Any, Tuple, Optional
import httpx
from data.config import API_KEY


class CaptchaSolver:
    """Async captcha solver for 2captcha API"""
    
    BASE_URL = "https://api.2captcha.com"
    
    def __init__(self, max_attempts: int = 30):
        self.api_key = API_KEY
        self.max_attempts = max_attempts
        self.client = httpx.AsyncClient(timeout=30)
    
    def decode_base64_image(self, base64_data: str) -> Optional[str]:
        """Decode base64 image and return clean data"""
        try:
            if base64_data.startswith("data:image"):
                base64_data = base64_data.split(",", 1)[1]
            return base64_data
        except Exception as e:
            print(f"Error decoding image: {str(e)}")
            return None
    
    async def solve_image_captcha(self, image_base64: str) -> Tuple[str, bool, Optional[int]]:
        """Solve image captcha using 2captcha API, returns (solution, success, task_id)"""
        try:
            captcha_data = {
                "clientKey": self.api_key,
                "softId": 4706,
                "task": {
                    "type": "ImageToTextTask",
                    "body": image_base64,
                    "phrase": False,
                    "case": True,
                    "numeric": 0,
                    "math": False,
                    "minLength": 4,
                    "maxLength": 8,
                    "comment": "Pay special attention to the letters and numbers.",
                },
            }

            resp = await self.client.post(
                f"{self.BASE_URL}/createTask", json=captcha_data
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("errorId") == 0:
                task_id = data.get("taskId")
                solution, success = await self.get_captcha_result(task_id)
                return solution, success, task_id
            return data.get("errorDescription"), False, None

        except httpx.HTTPStatusError as err:
            return f"HTTP error occurred: {err}", False, None
        except Exception as err:
            return f"An unexpected error occurred: {err}", False, None
    
    async def get_captcha_result(self, task_id: int | str) -> Tuple[str, bool]:
        """Get captcha solution result"""
        for _ in range(self.max_attempts):
            try:
                resp = await self.client.post(
                    f"{self.BASE_URL}/getTaskResult",
                    json={"clientKey": self.api_key, "taskId": task_id},
                )
                resp.raise_for_status()
                result = resp.json()

                if result.get("errorId") != 0:
                    return result.get("errorDescription"), False

                if result.get("status") == "ready":
                    if result["solution"].get("token"):
                        return result["solution"].get("token", ""), True
                    return result["solution"].get("text", ""), True

                await asyncio.sleep(3)

            except httpx.HTTPStatusError as err:
                return f"HTTP error occurred: {err}", False
            except Exception as err:
                return f"An unexpected error occurred: {err}", False

        return "Max time for solving exhausted", False
    
    async def report_bad(self, task_id: str | int) -> Tuple[Any, bool]:
        """Report incorrect captcha solution"""
        try:
            resp = await self.client.post(
                f"{self.BASE_URL}/reportIncorrect",
                json={"clientKey": self.api_key, "taskId": task_id},
            )
            resp.raise_for_status()
            return resp.json(), True
        except httpx.HTTPStatusError as err:
            return f"HTTP error occurred: {err}", False
        except Exception as err:
            return f"An unexpected error occurred: {err}", False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
