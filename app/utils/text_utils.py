from typing import List


def extract_keywords(text: str) -> List[str]:
    """
    텍스트에서 간단한 키워드를 추출합니다.
    
    Args:
        text (str): 입력 텍스트
        
    Returns:
        List[str]: 추출된 키워드 목록
    """
    # 실제 프로젝트에서는 더 복잡한 키워드 추출 로직을 구현할 수 있습니다.
    keywords = [word.strip() for word in text.split() if len(word.strip()) > 1]
    return keywords

def contains_any_keywords(text: str, keywords: List[str]) -> bool:
    """
    텍스트에 주어진 키워드 중 하나라도 포함되어 있는지 확인합니다.
    
    Args:
        text (str): 검사할 텍스트
        keywords (List[str]): 키워드 목록
        
    Returns:
        bool: 키워드 포함 여부
    """
    return any(keyword in text for keyword in keywords)

def create_formatted_list(items: List[str]) -> str:
    """
    항목들을 번호가 매겨진 목록 형식의 문자열로 변환합니다.
    
    Args:
        items (List[str]): 항목 목록
        
    Returns:
        str: 포맷팅된 문자열
    """
    return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
