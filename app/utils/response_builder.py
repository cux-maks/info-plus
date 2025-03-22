"""카카오톡 응답 생성을 위한 유틸리티 모듈.

이 모듈은 카카오톡 챗봇의 다양한 응답 형식을 생성하는 함수들을 제공합니다.
SimpleText, BasicCard, QuickReply 등 카카오톡 응답 포맷에 맞는 데이터 구조를 생성합니다.
"""

from typing import Any, Dict, List, Optional


def create_simple_text_response(text: str) -> Dict[str, Any]:
    """간단한 텍스트 응답을 생성합니다.

    카카오톡 SimpleText 응답 형식에 맞는 데이터 구조를 생성합니다.

    Args:
        text: 응답할 텍스트 메시지

    Returns:
        카카오톡 SimpleText 응답 포맷의 딕셔너리
    """
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": text
                    }
                }
            ]
        }
    }

def create_basic_card_response(
    title: str,
    description: str,
    thumbnail_url: Optional[str] = None
) -> Dict[str, Any]:
    """기본 카드 응답을 생성합니다.

    카카오톡 BasicCard 응답 형식에 맞는 데이터 구조를 생성합니다.
    썸네일 이미지는 선택적으로 추가할 수 있습니다.

    Args:
        title: 카드의 제목
        description: 카드의 설명 텍스트
        thumbnail_url: 카드에 표시될 썸네일 이미지의 URL (선택사항)

    Returns:
        카카오톡 BasicCard 응답 포맷의 딕셔너리
    """
    card = {
        "title": title,
        "description": description
    }

    if thumbnail_url:
        card["thumbnail"] = {"imageUrl": thumbnail_url}

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "basicCard": card
                }
            ]
        }
    }

def add_quick_replies(
    response: Dict[str, Any],
    quick_replies: List[Dict[str, str]]
) -> Dict[str, Any]:
    """응답에 빠른 응답(퀵리플라이) 버튼을 추가합니다.

    기존 응답 구조에 카카오톡 QuickReply 버튼 목록을 추가합니다.

    Args:
        response: 기존 카카오톡 응답 구조
        quick_replies: QuickReply 버튼 정보 목록

    Returns:
        QuickReply가 추가된 카카오톡 응답 구조
    """
    response["template"]["quickReplies"] = quick_replies
    return response
