"""텍스트 처리를 위한 유틸리티 모듈.

이 모듈은 텍스트 처리와 관련된 다양한 유틸리티 함수들을 제공합니다.
키워드 추출, 키워드 검색, 텍스트 포맷팅 등의 기능을 포함합니다.
"""

from typing import List


def extract_keywords(text: str) -> List[str]:
    """텍스트에서 키워드를 추출합니다.

    입력된 텍스트를 분석하여 의미있는 키워드들을 추출합니다.
    현재는 단순 공백 기준 분리 방식을 사용하며, 2글자 이상의 단어만 추출합니다.

    Args:
        text: 키워드를 추출할 입력 텍스트

    Returns:
        추출된 키워드 목록
    """
    # 실제 프로젝트에서는 더 복잡한 키워드 추출 로직을 구현할 수 있습니다.
    keywords = [word.strip() for word in text.split() if len(word.strip()) > 1]
    return keywords

def contains_any_keywords(text: str, keywords: List[str]) -> bool:
    """텍스트에 주어진 키워드들이 포함되어 있는지 확인합니다.

    입력된 텍스트에 키워드 목록 중 하나라도 포함되어 있는지 검사합니다.
    대소문자를 구분하여 검사합니다.

    Args:
        text: 검사할 대상 텍스트
        keywords: 검색할 키워드 목록

    Returns:
        키워드 포함 여부 (True/False)
    """
    return any(keyword in text for keyword in keywords)

def create_formatted_list(items: List[str]) -> str:
    """항목들을 번호가 매겨진 목록 형식의 문자열로 변환합니다.

    입력된 항목들을 "1. 항목1\n2. 항목2" 형식의 문자열로 변환합니다.
    빈 목록이 입력되면 빈 문자열을 반환합니다.

    Args:
        items: 포맷팅할 항목들의 목록

    Returns:
        번호가 매겨진 목록 형식의 문자열
    """
    return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
