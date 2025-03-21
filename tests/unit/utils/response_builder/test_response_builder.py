"""카카오톡 응답 생성 유틸리티에 대한 단위 테스트.

이 모듈은 카카오톡 챗봇의 응답 생성 유틸리티 함수들에 대한 단위 테스트를 포함합니다.
SimpleText, BasicCard, QuickReply 등 다양한 응답 형식 생성 함수들을 테스트합니다.
"""

import json
import os
from typing import Any, Dict

import pytest

from app.utils.response_builder import (
    add_quick_replies,
    create_basic_card_response,
    create_simple_text_response,
)


class TestResponseBuilder:
    """카카오톡 응답 생성 유틸리티에 대한 테스트 스위트.

    각 테스트 케이스는 외부 JSON 파일의 테스트 데이터를 사용하여
    response_builder.py 모듈의 응답 생성 함수들을 검증합니다.

    Attributes:
        test_data: JSON 파일에서 로드한 테스트 데이터
    """

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
            "response_builder_cases.json"
        )
        with open(test_data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_create_simple_text_response(self, test_data: Dict[str, Any]):
        """create_simple_text_response 함수에 대한 테스트.

        SimpleText 형식의 응답이 올바르게 생성되는지 검증합니다.

        Args:
            test_data: 테스트 케이스 데이터
        """
        case = test_data["simple_text"]
        result = create_simple_text_response(case["input"]["text"])
        assert result == case["expected"]

    def test_create_basic_card_response(self, test_data: Dict[str, Any]):
        """create_basic_card_response 함수에 대한 테스트.

        BasicCard 형식의 응답이 썸네일과 함께 올바르게 생성되는지 검증합니다.

        Args:
            test_data: 테스트 케이스 데이터
        """
        case = test_data["basic_card"]
        result = create_basic_card_response(
            title=case["input"]["title"],
            description=case["input"]["description"],
            thumbnail_url=case["input"]["thumbnail_url"]
        )
        assert result == case["expected"]

    def test_create_basic_card_response_without_thumbnail(self, test_data: Dict[str, Any]):
        """썸네일이 없는 create_basic_card_response 함수에 대한 테스트.

        BasicCard 형식의 응답이 썸네일 없이 올바르게 생성되는지 검증합니다.

        Args:
            test_data: 테스트 케이스 데이터
        """
        case = test_data["basic_card"]
        result = create_basic_card_response(
            title=case["input"]["title"],
            description=case["input"]["description"]
        )
        expected = case["expected"].copy()
        del expected["template"]["outputs"][0]["basicCard"]["thumbnail"]
        assert result == expected

    def test_add_quick_replies(self, test_data: Dict[str, Any]):
        """add_quick_replies 함수에 대한 테스트.

        기존 응답에 QuickReply 버튼들이 올바르게 추가되는지 검증합니다.

        Args:
            test_data: 테스트 케이스 데이터
        """
        case = test_data["quick_replies"]
        result = add_quick_replies(
            response=case["input"]["response"],
            quick_replies=case["input"]["quick_replies"]
        )
        assert result == case["expected"]
