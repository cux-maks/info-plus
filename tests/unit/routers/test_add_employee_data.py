from unittest.mock import MagicMock, patch

import pytest

from app.utils.insert_employee_data import fetch_and_insert_recent_jobs


@pytest.fixture
def mock_db_session():
    """SQLAlchemy DB 세션을 모킹합니다."""
    mock = MagicMock()
    mock.add = MagicMock()
    mock.commit = MagicMock()
    return mock

@patch("app.utils.insert_employee_data.requests.get")
def test_fetch_and_insert_recent_jobs_success(mock_get, mock_db_session):
    """API 응답이 정상적이고, 데이터가 잘 저장되는 경우 테스트"""

    mock_response_data = {
        "result": [
            {
                "recrutPblntSn": "12345678",
                "recrutPbancTtl": "채용공고 제목 1",
                "instNm": "테스트 기관 1",
                "pbancBgngYmd": "20240501",
                "pbancEndYmd": "20240515",
                "recrutSe": "R2010",
                "ncsCdLst": "R600001",
                "hireTypeLst": "R1010"
            },
            {
                "recrutPblntSn": "55667788",
                "recrutPbancTtl": "채용공고 제목 5",
                "instNm": "테스트 기관 5",
                "pbancBgngYmd": "20240901",
                "pbancEndYmd": "20240915",
                "recrutSe": "R2010",
                "ncsCdLst": "R600002",
                "hireTypeLst": "R1010,R1020"  # 중복된 고용형태
            },
            {
                "recrutPblntSn": "77889900",
                "recrutPbancTtl": "채용공고 제목 6",
                "instNm": "테스트 기관 6",
                "pbancBgngYmd": "20241001",
                "pbancEndYmd": "20241015",
                "recrutSe": "R2030",
                "ncsCdLst": "R600005,R600020",  # 중복된 NCS 코드
                "hireTypeLst": "R1030"
            },
            {
                "recrutPblntSn": "99001122",
                "recrutPbancTtl": "채용공고 제목 7",
                "instNm": "테스트 기관 7",
                "pbancBgngYmd": "20241101",
                "pbancEndYmd": "20241115",
                "recrutSe": "R2010",  # 신입
                "ncsCdLst": "R600002,R600005,R600020",  # 중복된 NCS 코드
                "hireTypeLst": "R1010,R1040"  # 중복된 고용형태
            }
        ]
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response_data

    inserted = fetch_and_insert_recent_jobs(days=1, db_session=mock_db_session)

    assert inserted == 4
    assert mock_db_session.add.call_count == 17  # 4개의 공고 + 7개의 카테고리 + 6개의 고용형태
    mock_db_session.commit.assert_called_once()

@patch("app.utils.insert_employee_data.requests.get")
def test_fetch_and_insert_recent_jobs_api_fail(mock_get, mock_db_session):
    """API가 실패 상태 코드를 반환할 경우 테스트"""
    mock_get.return_value.status_code = 500
    inserted = fetch_and_insert_recent_jobs(days=1, db_session=mock_db_session)

    assert inserted == 0
    mock_db_session.add.assert_not_called()

@patch("app.utils.insert_employee_data.requests.get")
def test_fetch_and_insert_recent_jobs_invalid_json(mock_get, mock_db_session):
    """응답 JSON 파싱 실패 시 테스트"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.side_effect = ValueError("Invalid JSON")

    inserted = fetch_and_insert_recent_jobs(days=1, db_session=mock_db_session)

    assert inserted == 0
    mock_db_session.add.assert_not_called()
