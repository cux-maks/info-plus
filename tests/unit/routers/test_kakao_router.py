import json
import os
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestKakaoRouter:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def test_data(self) -> Dict[str, Any]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_data_path = os.path.join(
            current_dir,
            "test_data",
            "router_cases.json"
        )
        with open(test_data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_handle_greeting_message(self, client: TestClient, test_data: Dict[str, Any]):
        """
        인사 메시지 처리 테스트
        """
        case = test_data["handle_message"]["greeting"]
        response = client.post("/kakao/message", json=case["input"])
        assert response.status_code == 200
        assert response.json() == case["expected"]

    def test_handle_help_message(self, client: TestClient, test_data: Dict[str, Any]):
        """
        도움말 메시지 처리 테스트
        """
        case = test_data["handle_message"]["help"]
        response = client.post("/kakao/message", json=case["input"])
        assert response.status_code == 200
        assert response.json() == case["expected"]

    def test_handle_unknown_message(self, client: TestClient):
        """
        알 수 없는 메시지 처리 테스트
        """
        response = client.post("/kakao/message", json={
            "intent": {},
            "userRequest": {
                "utterance": "알 수 없는 메시지"
            },
            "bot": {},
            "action": {}
        })
        assert response.status_code == 200
        assert "안녕하세요! 무엇을 도와드릴까요?" in response.json()["template"]["outputs"][0]["simpleText"]["text"]
