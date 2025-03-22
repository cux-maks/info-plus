"""텍스트 유틸리티 모듈에 대한 단위 테스트.

이 모듈은 text_utils.py 모듈의 각 함수들에 대한 단위 테스트를 포함합니다.
테스트 데이터는 외부 JSON 파일에서 로드하여 사용합니다.
"""

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
    """텍스트 유틸리티 함수들에 대한 테스트 스위트.

    각 테스트 케이스는 외부 JSON 파일의 테스트 데이터를 사용하여
    text_utils.py 모듈의 함수들을 검증합니다.

    Attributes:
        test_data: JSON 파일에서 로드한 테스트 데이터
    """

    @pytest.fixture
    def test_data(self) -> Dict[str, Any]:
        """테스트 데이터를 로드하는 fixture.

        Returns:
            JSON 파일에서 로드한 테스트 케이스 데이터
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_data_path = os.path.join(
            current_dir,
            "test_data",
            "text_utils_cases.json"
        )
        with open(test_data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_extract_keywords(self, test_data: Dict[str, Any]):
        """extract_keywords 함수에 대한 테스트.

        주어진 텍스트에서 키워드가 올바르게 추출되는지 검증합니다.

        Args:
            test_data: 테스트 케이스 데이터
        """
        case = test_data["extract_keywords"]
        result = extract_keywords(case["input"]["text"])
        assert result == case["expected"]

    def test_contains_any_keywords(self, test_data: Dict[str, Any]):
        """contains_any_keywords 함수에 대한 테스트.

        텍스트에 키워드 포함 여부가 올바르게 확인되는지 검증합니다.

        Args:
            test_data: 테스트 케이스 데이터
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
        assert not result

    def test_create_formatted_list(self, test_data: Dict[str, Any]):
        """create_formatted_list 함수에 대한 테스트.

        항목 목록이 올바른 형식의 문자열로 변환되는지 검증합니다.

        Args:
            test_data: 테스트 케이스 데이터
        """
        case = test_data["create_formatted_list"]
        result = create_formatted_list(case["input"]["items"])
        assert result == case["expected"]

        # 빈 리스트 테스트
        result = create_formatted_list([])
        assert result == ""
