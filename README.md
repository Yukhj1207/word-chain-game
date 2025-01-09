##싱글과 멀티플레이가 가능한 api활용 끝말잇기 게임
##Single and multi-player compatible API for playing a word chain game.

*******************************************게임 규칙 (Game Rules)********************************************
1. 게임의 목표 (Objective)
 마지막으로 나온 단어의 마지막 글자로 시작하는 단어를 제한 시간 안에 입력하세요.
 올바른 단어를 입력하면 점수를 얻고, 상대방이 더 이상 단어를 이어가지 못하면 승리합니다.
 Continue the chain by entering a word that starts with the last letter of the previous word within the time limit.
 Earn points for valid words, and win if your opponent can no longer continue the chain.

2. 게임의 방식 (Gameplay Modes)
 싱글플레이어 (Singleplayer): AI와 대결합니다.
 멀티플레이어 (Multiplayer): 친구와 네트워크 연결을 통해 대결합니다.
 Singleplayer: Compete against the AI.
 Multiplayer: Play with a friend over a network connection.

3. 끝말잇기 규칙 (Rules)
 단어는 한국어 명사만 허용됩니다.
 이미 사용된 단어는 다시 사용할 수 없습니다.
 두음법칙에 의해 정당히 들어맞는 단어는 허용됩니다.
 제한 시간 내에 단어를 입력하지 못하면 패배합니다.
 Only Korean nouns are allowed.
 Duplicate previously used words are not allowed.
 Words correctly matching the "두음법칙" rule are acceptable.
 Failure to enter a word within the time limit results in a loss.
*************************************************************************************************************


********************************************실행 방법 (How to Run)*******************************************
1. 레포지토리 클론(Clone the repository)
   git clone https://github.com/hyunjin1207/word-chain-game.git
   cd word-chain-game

2. Python 실행(Run the game)
   python word_chain_game.py

3. 게임 플레이
   싱글플레이: AI와 대결
   멀티플레이: 네트워크로 친구와 대결
   Singleplayer: Compete with AI.
   Multiplayer: Play with a friend over the network.
*************************************************************************************************************


*****************************한국어기초사전 사용 (Korean Basic Dictionary Usage)*****************************
 본 게임은 한국어기초사전의 데이터를 참고하여 단어를 검증합니다.
   한국어기초사전 사이트: https://krdict.korean.go.kr/
 일부 단어는 누락되어 있을 수 있으니 참고 바랍니다.
 This game uses the Korean Basic Dictionary to validate words.
   Korean Basic Dictionary website: https://krdict.korean.go.kr/
 Please note that some words may be missing due to limitations in the dictionary.
*************************************************************************************************************


********************************************기술 스택 (Built With********************************************
 Python 3.x: 메인 프로그래밍 언어
 Tkinter: GUI 구축에 사용
 Socket Programming: 멀티플레이 네트워크 구현
 Python 3.x: Main programming language
 Tkinter: Used for the graphical user interface
 Socket Programming: Implemented multiplayer network connection
*************************************************************************************************************


*********************************************한계 (Limitations)*********************************************
 현재 영어 단어는 게임에서 사용이 불가능합니다.
 한국어기초사전을 활용하고 있지만 일부 단어가 누락될 가능성이 있습니다.
 Currently, English words are not supported in the game.
 While the game relies on the Korean Basic Dictionary, there is a possibility that some words may be excluded.
*************************************************************************************************************


*********************************************기여 (Contribution)*********************************************
1. 레포지토리 포크(Fork the repository)
   git fork https://github.com/hyunjin1207/word-chain-game.git

2. 새로운 브랜치 생성(Create a new branch)
   git checkout -b feature/your-feature-name

3. 변경 사항 커밋(Commit your changes)
   git commit -m "Add your message here"

4. 푸시 및 PR 제출(Push and submit a PR)
   git push origin feature/your-feature-name
*************************************************************************************************************
