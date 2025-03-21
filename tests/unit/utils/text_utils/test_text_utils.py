import json
import os
from typing import Any, Dict

import pytest

from app.utils.text_utils import (
    contains_any_keywords,
    create_formatted_list,
    extract_keywords,
)


class TestTextUtils:
    @pytest.fixture
    def test_data(self) -> Dict[str, Any]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_data_path = os.path.join(
            current_dir,
            "test_data",
            "text_utils_cases.json"
        )
        with open(test_data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_extract_keywords(self, test_data: Dict[str, Any]):
        """
        extract_keywords 함수 테스트
        """
        case = test_data["extract_keywords"]
        result = extract_keywords(case["input"]["text"])
        assert result == case["expected"]

    def test_contains_any_keywords(self, test_data: Dict[str, Any]):
        """
        contains_any_keywords 함수 테스트
        """
        case = test_data["contains_any_keywords"]
        result = contains_any_keywords(
            text=case["input"]["text"],
            keywords=case["input"]["keywords"]
        )
        assert result == case["expected"]

        # 키워드가 없는 경우 테스트
        result = contains_any_keywords(
            text="전혀 다른 내용입니다",
            keywords=case["input"]["keywords"]
        )
        assert result == False

    def test_create_formatted_list(self, test_data: Dict[str, Any]):
        """
        create_formatted_list 함수 테스트
        """
        case = test_data["create_formatted_list"]
        result = create_formatted_list(case["input"]["items"])
        assert result == case["expected"]

        # 빈 리스트 테스트
        result = create_formatted_list([])
        assert result == ""
