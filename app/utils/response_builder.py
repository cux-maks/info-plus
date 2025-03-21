from typing import Any, Dict, List, Optional


def create_simple_text_response(text: str) -> Dict[str, Any]:
    """
    간단한 텍스트 응답을 생성합니다.
    
    Args:
        text (str): 응답할 텍스트
        
    Returns:
        Dict[str, Any]: 카카오톡 응답 포맷
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
    """
    기본 카드 응답을 생성합니다.
    
    Args:
        title (str): 카드 제목
        description (str): 카드 설명
        thumbnail_url (str, optional): 썸네일 이미지 URL
        
    Returns:
        Dict[str, Any]: 카카오톡 응답 포맷
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
    """
    응답에 빠른 응답(퀵리플라이)을 추가합니다.
    
    Args:
        response (Dict[str, Any]): 기존 응답
        quick_replies (List[Dict[str, str]]): 퀵리플라이 목록
        
    Returns:
        Dict[str, Any]: 퀵리플라이가 추가된 응답
    """
    response["template"]["quickReplies"] = quick_replies
    return response
