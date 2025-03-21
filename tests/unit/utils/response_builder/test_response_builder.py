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
    @pytest.fixture
    def test_data(self) -> Dict[str, Any]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_data_path = os.path.join(
            current_dir,
            "test_data",
            "response_builder_cases.json"
        )
        with open(test_data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_create_simple_text_response(self, test_data: Dict[str, Any]):
        """
        create_simple_text_response 함수 테스트
        """
        case = test_data["simple_text"]
        result = create_simple_text_response(case["input"]["text"])
        assert result == case["expected"]

    def test_create_basic_card_response(self, test_data: Dict[str, Any]):
        """
        create_basic_card_response 함수 테스트
        """
        case = test_data["basic_card"]
        result = create_basic_card_response(
            title=case["input"]["title"],
            description=case["input"]["description"],
            thumbnail_url=case["input"]["thumbnail_url"]
        )
        assert result == case["expected"]

    def test_create_basic_card_response_without_thumbnail(self, test_data: Dict[str, Any]):
        """
        썸네일 없는 create_basic_card_response 함수 테스트
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
        """
        add_quick_replies 함수 테스트
        """
        case = test_data["quick_replies"]
        result = add_quick_replies(
            response=case["input"]["response"],
            quick_replies=case["input"]["quick_replies"]
        )
        assert result == case["expected"]
