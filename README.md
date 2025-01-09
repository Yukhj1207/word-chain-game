# 싱글과 멀티플레이가 가능한 api활용 끝말잇기 게임

## 게임 규칙
 한국어기초사전에 등제된 단어여야 합니다.
 이미 사용된 단어는 다시 사용할 수 없습니다.
 두음법칙을 적용해 ㄴ,ㄹ을 ㅇ으로 변경할 수 있습니다.
 제한 시간 내에 단어를 입력하지 못하면 패배합니다.

## 실행 방법
1. pip 을 사용해 requests 모듈을 설치합니다.
2. [한국어기초사전 오픈 API 서비스 소개 페이지](https://krdict.korean.go.kr/openApi/openApiInfo)로 가 API키 발급을 신청합니다.
3. 발급받은 API키를 check_word_validity,has_noun,fetch_word_from_api 함수의
   apikey = '발급받은 API키 붙여넣는곳' 부분의 (발급받은 API키 붙여넣는곳)를 지우고 발급받은 API키를 넣습니다.
4. 스크립트를 실행합니다.

## 참고사항
 1. 본 게임은 한국어기초사전의 데이터를 참고하여 단어를 검증합니다.
    한국어기초사전 사이트: ![](https://krdict.korean.go.kr/)
    일부 단어는 누락되어 있을 수 있으니 참고 바랍니다.
 2. 학교 포트폴리오용으로 제작된 코드입니다.
 3. 이 코드에서 이용하는 API는 하루에 25,000건만 호출이 가능합니다.
 4. pdjdev님의 코드를 참고하여 만들어졌습니다.
    참고 주소: ![](https://github.com/pdjdev/py_endtoend?tab=readme-ov-file)
