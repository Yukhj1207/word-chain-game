# Word Chain Game – Single/Multiplayer with API & AI Support

## Overview
This is a Korean word chain game implemented in Python.  
It features both **single-player (against AI)** and **multiplayer (2 players over socket communication)** modes.  
Words are validated using the official **Korean Basic Dictionary Open API**, and an optional AI (GPT) can play as the opponent in single mode.

Built as a personal portfolio project by a high school software student, it showcases networking, GUI, API integration, and OOP design.

## Features
- Real-time multiplayer over local network (socket)
- AI opponent using GPT (single mode)
- Korean word validation via external API
- Typing timer / win-lose detection
- GUI with `tkinter`
- Implements sound Korean grammar rules (두음법칙 included)
- Object-oriented structure

## Tech Stack
- Python 3.11
- `socket`, `threading`, `tkinter`
- [Korean Basic Dictionary Open API](https://krdict.korean.go.kr/openApi/openApiInfo)
- GPT (OpenAI API)
- OOP architecture

## How to Run

### Requirements
- Python 3.11
- `requests` module (install with `pip install requests`)
- API key from [Korean Dictionary Open API](https://krdict.korean.go.kr/openApi/openApiInfo)

### Setup
1. Replace the placeholder `apikey = 'YOUR_API_KEY_HERE'` in the following functions:
   - `check_word_validity()`
   - `has_noun()`
   - `fetch_word_from_api()`

2. Connect both devices to the same Wi-Fi network (for multiplayer).
3. Run the Python script:
   - Single-player: run the script and choose AI mode
   - Multiplayer: one device acts as server, another as client
   - Enter IP address of the server when prompted

> GPT usage for AI mode requires OpenAI key and separate setup.

## Gameplay
[Gameplay Video (temporarily unavailable)](https://github.com/user-attachments/assets/6b94cbd6-86fb-44d3-b168-2ba11dc651f8.mp4)  
Screenshots will be added in next update

## Author
- Name: Hyunjin Yuk (육현진)
- School: Dankook University Software High School (1st year)
- Note: Built entirely solo as a portfolio and learning project
- Code reference inspiration: [pdjdev/py_endtoend](https://github.com/pdjdev/py_endtoend)

## Project Duration
May 2024 – September 2024

## Known Limitations
- Dictionary API may miss some valid words
- API has a daily limit of 25,000 calls
- Multiplayer only supports local (LAN) connections for now

## Version
- Current: `v0.1`
- Upcoming: `v0.2` (Improved UI, GPT fallback handling, modular refactor)

---

## Korean (한국어 요약)

- 이 게임은 소켓 통신과 API를 활용한 끝말잇기 게임입니다.
- 싱글플레이 모드는 GPT AI와 대결 가능
- 단어 검증은 한국어기초사전 OpenAPI 사용
- 네트워크, API, 객체지향, GUI까지 포함된 프로젝트입니다.
