"""카카오톡 챗봇 라우터에 대한 단위 테스트.

이 모듈은 카카오톡 챗봇의 메시지 처리 라우터에 대한 단위 테스트를 포함합니다.
FastAPI TestClient를 사용하여 엔드포인트를 테스트하며, 테스트 데이터는 외부 JSON 파일에서 로드합니다.
"""

import json
import os
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestKakaoRouter:
    """카카오톡 챗봇 라우터에 대한 테스트 스위트.

    각 테스트 케이스는 FastAPI TestClient를 사용하여
    카카오톡 메시지 처리 엔드포인트의 동작을 검증합니다.

    Attributes:
        client: FastAPI 테스트 클라이언트
        test_data: JSON 파일에서 로드한 테스트 데이터
    """

    @pytest.fixture
    def client(self):
        """FastAPI 테스트 클라이언트를 생성하는 fixture.

        Returns:
            TestClient: FastAPI 애플리케이션의 테스트 클라이언트
        """
        return TestClient(app)

    @pytest.fixture
    def test_data(self) -> Dict[str, Any]:
        """테스트 데이터를 로드하는 fixture.

        Returns:
            Dict[str, Any]: JSON 파일에서 로드한 테스트 케이스 데이터
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_data_path = os.path.join(
            current_dir,
            "test_data",
            "router_cases.json"
        )
        with open(test_data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_handle_greeting_message(self, client: TestClient, test_data: Dict[str, Any]):
        """인사 메시지 처리 테스트.

        인사말에 대한 챗봇의 응답이 올바르게 처리되는지 검증합니다.

        Args:
            client: FastAPI 테스트 클라이언트
            test_data: 테스트 케이스 데이터
        """
        case = test_data["handle_message"]["greeting"]
        response = client.post("/kakao/message", json=case["input"])
        assert response.status_code == 200
        assert response.json() == case["expected"]

    def test_handle_help_message(self, client: TestClient, test_data: Dict[str, Any]):
        """도움말 메시지 처리 테스트.

        도움말 요청에 대한 챗봇의 응답이 올바르게 처리되는지 검증합니다.

        Args:
            client: FastAPI 테스트 클라이언트
            test_data: 테스트 케이스 데이터
        """
        case = test_data["handle_message"]["help"]
        response = client.post("/kakao/message", json=case["input"])
        assert response.status_code == 200
        assert response.json() == case["expected"]

    def test_handle_unknown_message(self, client: TestClient):
        """알 수 없는 메시지 처리 테스트.

        정의되지 않은 메시지에 대한 챗봇의 기본 응답이 올바르게 처리되는지 검증합니다.

        Args:
            client: FastAPI 테스트 클라이언트
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
