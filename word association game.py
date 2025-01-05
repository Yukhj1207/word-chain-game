import socket
import threading
import ipaddress
import requests
import random
import time
import xml.etree.ElementTree as ET
from tkinter import *
from tkinter import font
from tkinter import messagebox

#로컬 IP 주소 검색
network_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
network_socket.connect(("8.8.8.8", 80))
local_ip = network_socket.getsockname()[0]
network_socket.close()

class Game:
    def __init__(self,ui):
        self.ui = ui
        self.word_list = []
        self.next_letter_for_message = ''
        self.next_letter_for_data = ''
        self.next_letter_for_ai_word = ''
        self.user_word = ''
        self.my_word_entry_button_clicked = False
        self.start_time = None
        self.my_remaining_time = 0
        self.doeum_rules = {}
        self.ai_word = ''
    
    #다른 메서드에서 소켓을 가져오는 함수
    def set_global_socket(self):
        self.global_socket = game_connection.get_global_socket()
    
    #게임을 다시 시작하기 위해 리셋하는 함수
    def reset_game(self):
        self.start_time = None
        self.word_list = []
        self.next_letter_for_message = ''
        self.next_letter_for_data = ''
        self.user_word = ''
        self.my_word_entry_button_clicked = False
        Loading.set_stop_connecting_animate(True)
        connecting_label.config(text='')
        word_list_listbox.delete(0, END)
        rel_word_label.config(text='')
        my_word_entry.delete(0, END)
        my_word_entry.config(state='disabled')
        my_word_entry_button.config(state='disabled')
        peer_ip_entry_button.place_forget()
        peer_ip_entry_button_label.place_forget()
        peer_ip_entry.place_forget()
        my_timer_label.config(bg='#D8D8D8')
        my_timer_bar.place(x=82,y=267,width=276,height=15)
        my_timer_bar.config(text='10')
        try:
            if self.global_socket:
                self.global_socket.shutdown
                self.global_socket.close()
        except NameError:
            pass
        except AttributeError:
            pass
    
    #게임 종료 후 재시작 여부에 따라 화면을 전환하거나 게임을 초기화 하는 함수
    def decide_re_game(self,result, socket_name):
        if socket_name == '':
            if result:
                self.ui.show_prev_frm(in_game_frm, loading_frm, '')
                Loading.set_stop_loading_animate(False)
                Loading.loading_animate()
                word_list_listbox.delete(0, END)
                rel_word_label.config(text="")
                my_word_entry.config(text="")
            else:
                self.ui.show_prev_frm(in_game_frm, main_menu_frm, '')
        elif result:
            self.ui.show_prev_frm(in_game_frm, connecting_frm, '')
            Loading.set_stop_connecting_animate(False)
            Loading.connecting_animate()
            word_list_listbox.delete(0, END)
            rel_word_label.config(text="")
            my_word_entry.config(text="")
            if socket_name == 'conn':
                window.after(2000, game_connection.start_server_thread)
            else:
                window.after(2000, game_connection.start_client_thread)
                peer_ip_entry_button.place(x=364,y=336,width=34,height=28)
                peer_ip_entry_button_label.place(x=363,y=335,width=36,height=30)
                peer_ip_entry.place(x=201, y=335, width=162, height=30)      
        else:
            self.ui.show_prev_frm(in_game_frm, main_menu_frm, '')
    
    #단어 유무 검증 함수
    def check_word_validity(self,query):
        apikey = '8015501B7F4DA8A4D78B18B2CF957C43'
        url = f'https://krdict.korean.go.kr/api/search?key={apikey}&part=word&q={query}'  #한국어기초사전 주소
        response = requests.get(url)
        if response.status_code == 200: #HTTP 요청 응답 확인
            result = response.text
            if '<error>' in result:
                return {'exists': False}
            total_start = result.find('<total>') + len('<total>')
            total_end = result.find('</total>')
            try:
                total = int(result[total_start:total_end])
            except ValueError:
                return {'exists': False}
            if total == 0:
                return {'exists': False}
            origin_start = result.find('<origin>') + len('<origin>')
            origin_end = result.find('</origin>')
            origin = result[origin_start:origin_end]
            is_hanja_word = any(self.is_hanja_character(char) for char in origin)
            pos = self.has_noun(query)
            return {'exists': True, 'pos': pos, 'origin':is_hanja_word} #exists:존재 여부, pos:품사, origin:어휘 유형
        else:
            return {'exists': False}

    def has_noun(self,word):
        apikey = '8015501B7F4DA8A4D78B18B2CF957C43'
        url = f'https://krdict.korean.go.kr/api/search?key={apikey}&part=word&q={word}'  # XML 형식으로 요청
        response = requests.get(url)
        if response.status_code == 200:
            try:
                root = ET.fromstring(response.text)
                word_info = root
            except ET.ParseError:
                return None
        else:
            return None
        items = word_info.findall('.//item')
        for item in items:
            pos = item.find('pos').text
            if pos == '명사':
                return '명사'
        return False

    #두음법칙인지 확인하는 함수
    def is_doeum_applicable(self,word,word_info,prev_word):
        self.doeum_rules = {    #'ㄴ','ㄹ' 의 두음법칙
            "녀": "여",
            "뇨": "요",
            "뉴": "유",
            "니": "이",
            "랴": "야",
            "려": "여",
            "례": "예",
            "료": "요",
            "류": "유",
            "리": "이",
        }
        if word_info['origin']:
            if prev_word in self.doeum_rules and self.doeum_rules[prev_word] == word[0]:
                return True
            else:
                return False

    #한자어인지 확인하는 함수
    def is_hanja_character(self,char):
        return (
            '\u4e00' <= char <= '\u9fff' or  # 기본 한자
            '\u3400' <= char <= '\u4dbf' or  # 확장 A
            '\u20000' <= char <= '\u2a6df' or  # 확장 B
            '\u2a700' <= char <= '\u2b73f' or  # 확장 C
            '\u2b740' <= char <= '\u2b81f' or  # 확장 D
            '\u2b820' <= char <= '\u2ceaf' or  # 확장 E
            '\u2ceb0' <= char <= '\u2ebef'    # 확장 F
        )

    #단어 적는 엔트리를 비활성화하는 함수
    def disable_my_word_entry(self):
        message = my_word_entry.get().strip()
        #적은 메시지가 한글자 이하라면 비활성화하지 않음
        if not message or len(message) == 1:
            my_word_entry.delete(0, END)
            return
        self.user_word = message
        self.my_word_entry_button_clicked = True
        my_word_entry_button.config(text='')
        my_word_entry.delete(0, END)
        my_word_entry.config(state='disabled')
        my_word_entry_button.config(state='disabled')
        my_timer_label.config(bg='#D8D8D8')
        timer.set_stop_my_timer(True)
        timer.set_stop_singleplay_timer(True)

    # 시작 글자로 시작하는 단어를 검색하는 함수
    def fetch_word_from_api(self, start_char,difficulty):
        apikey = '8015501B7F4DA8A4D78B18B2CF957C43'
        url = f'https://krdict.korean.go.kr/api/search?key={apikey}&part=word&q={start_char}*&num=100'
        response = requests.get(url)
        if response.status_code == 200:
            result = response.text
            words = []
            start = 0
            while True:
                word_start = result.find('<word>', start)
                if word_start == -1:
                    break
                word_end = result.find('</word>', word_start)
                word = result[word_start + len('<word>'):word_end]
                pos_start = result.find('<pos>', word_end)
                pos_end = result.find('</pos>', pos_start)
                pos = result[pos_start + len('<pos>'):pos_end]
                # 명사만 추가
                if pos == "명사" and len(word) >= 2:
                    words.append(word)
                start = word_end
            return self.filter_words_by_difficulty(words,difficulty)
        return []

    # 난이도별 단어 필터링
    def filter_words_by_difficulty(self, words, difficulty):
        if difficulty == 0:
            # 쉬운 단어: 2~3 글자
            fixed_words = [word for word in words if 2 <= len(word) <= 3]
        elif difficulty == 1:
            # 보통 단어: 4~5 글자
            fixed_words = [word for word in words if 4 <= len(word) <= 5]
            if len(fixed_words) == 0:
                fixed_words = [word for word in words if 2 <= len(word) <= 3]
        elif difficulty == 2:
            # 어려운 단어: 6 글자 이상
            fixed_words = [word for word in words if len(word) >= 6]
            if len(fixed_words) == 0:
                fixed_words = [word for word in words if 4 <= len(word) <= 5]
                if len(fixed_words) == 0:
                    fixed_words = [word for word in words if 2 <= len(word) <= 3]
        
        # 랜덤으로 하나 선택
        return random.sample(fixed_words, len(fixed_words)) if fixed_words else []

    # AI의 단어 선택 함수
    def select_ai_word(self, start_char,difficulty):
        words = self.fetch_word_from_api(start_char,difficulty)
        if words:
            return random.choice(words)  # 랜덤으로 단어 선택
        return None  # 사용할 단어가 없을 경우

    #싱글플레이의 과정과 승패를 결정하는 함수
    def singleplay_player(self,first_interation):
        if first_interation:
            timer.start_singleplayer_timer(15)
        else:
            timer.start_singleplayer_timer(self.my_remaining_time)
        my_word_entry.config(state='normal')
        my_word_entry_button.config(state='normal')
        my_word_entry_button.config(text='완료')
        my_timer_label.config(bg='#2E64FE')
        my_word_entry.focus_set()
        while not self.my_word_entry_button_clicked: #단어를 적을 때 까지 기다림
            in_game_frm.update()
        self.my_word_entry_button_clicked = False
        rel_word_label.config(text=self.user_word)
        rel_word_label.config(fg='blue')
        word_list_listbox.insert(END,self.user_word)
        word_list_listbox.yview(END)
        word_list_listbox.itemconfig(END, {'fg': 'blue'})
        user_word_info = self.check_word_validity(self.user_word) #플레이어 단어의 정보를 저장
        rel_word_label['text'] = self.user_word
        window.update()
        if not user_word_info['exists']: #플레이어 단어가 존재하지 않을때
            result = messagebox.askyesno("패배", f"단어 '{self.user_word}'은/는 존재하지 않습니다.\n다시 하시겠습니까?")
            self.reset_game()
            self.decide_re_game(result,'')
            return True
        elif user_word_info['pos'] != '명사': #플레이어 단어가 명사가 아닐때
            result = messagebox.askyesno("패배", f"단어 '{self.user_word}'은/는 명사가 아닙니다.\n다시 하시겠습니까?")
            self.reset_game()
            self.decide_re_game(result,'')
            return True
        if not first_interation:
            if self.user_word[0] != self.next_letter_for_ai_word: #플레이어 단어의 첫글자가의 단어의 마지막 글자와 일치하지 않을때
                doeum_result = self.is_doeum_applicable(self.user_word,user_word_info,self.next_letter_for_data)
                if not doeum_result:
                    result = messagebox.askyesno("패배", f"단어를 잘못 연결했습니다.\n다시 하시겠습니까?")
                    self.reset_game()
                    self.decide_re_game(result,'')
                    return True
            elif self.user_word in self.word_list: #플레이어 단어가 이미 사용한 단어일때
                result = messagebox.askyesno("패배", f"단어 '{self.user_word}'은/는 이미 사용되었습니다.\n다시 하시겠습니까?")
                self.reset_game()
                self.decide_re_game(result,'')
                return True
        self.my_remaining_time = timer.get_timer_duration(self.user_word)
        self.word_list.append(self.user_word)
        self.next_letter_for_message = self.user_word[-1]
        difficulty = ui.get_current_index()
        ai_word = self.select_ai_word(self.next_letter_for_message,difficulty)
        if not ai_word:
            result = messagebox.askyesno("승리", f"AI가 단어를 찾지 못했습니다.\n다시 하시겠습니까?")
            self.reset_game()
            self.decide_re_game(result,'')
            return True
        rel_word_label.config(text=ai_word)
        rel_word_label.config(fg='black')
        word_list_listbox.insert(END,'    '+str(ai_word))
        word_list_listbox.yview(END)
        self.word_list.append(ai_word)
        self.next_letter_for_ai_word = ai_word[-1]
        return False
        
    #멀티플레이의 과정과 승패를 결정하는 함수
    def process_multiplay_turn(self,first_iteration,socket_type,my_socket):
        Loading.set_stop_connecting_animate(True)
        if socket_type == 'conn': #서버일때
            if first_iteration: #첫번째턴이라면
                timer.start_peer_timer(15,my_socket,socket_type)
            else:
                timer.start_peer_timer(self.my_remaining_time,my_socket, socket_type)
            try:
                self.data = my_socket.recv(1024).decode() #상대에게 단어를 받음
                timer.set_stop_peer_timer(True)
            except TimeoutError:
                return True
            if not self.data:
                my_socket.close()
                result = messagebox.askyesno("승리", "상대방이 게임을 종료했습니다.\n다시 하시겠습니까?")
                self.reset_game()
                self.decide_re_game(result,socket_type)
                return True
            data_info = self.check_word_validity(self.data) #상대에게 받은 단어의 정보를 저장
            rel_word_label.config(text=self.data)
            rel_word_label.config(fg='black')
            word_list_listbox.insert(END,'    '+str(self.data))
            word_list_listbox.yview(END)
            if not data_info['exists']: #상대에게 받은 단어가 존재하지 않을때
                my_socket.close()
                result = messagebox.askyesno("승리", f"상대방의 단어 '{self.data}'은/는 존재하지 않습니다.\n다시 하시겠습니까?")
                self.reset_game()
                self.decide_re_game(result,socket_type)
                return True
            elif data_info['pos'] != '명사': #상대에게 받은 단어가 명사가 아닐때
                my_socket.close()
                result = messagebox.askyesno("승리", f"상대방의 단어 '{self.data}'은/는 명사가 아닙니다.\n다시 하시겠습니까?")
                self.reset_game()
                self.decide_re_game(result,socket_type)
                return True
            elif not first_iteration and self.data[0] != self.next_letter_for_message:  #상대 단어의 첫글자가 플레이어 단어의 마지막 글자와 일치하지 않을때
                doeum_result = self.is_doeum_applicable(self.data,data_info,self.next_letter_for_message)
                if not doeum_result:
                    my_socket.close()
                    result = messagebox.askyesno("승리", "상대방이 단어를 잘못 연결했습니다.\n다시 하시겠습니까?")
                    self.reset_game()
                    self.decide_re_game(result,socket_type)
                    return True
            elif self.data in self.word_list: #상대 단어가 이미 사용한 단어일때
                my_socket.close()
                result = messagebox.askyesno("승리", f"상대방의 단어 '{self.user_word}'은/는 이미 사용되었습니다.\n다시 하시겠습니까?")
                self.reset_game()
                self.decide_re_game(result,socket_type)
                return True
            peer_remaining_time = timer.get_timer_duration(self.data)
            self.word_list.append(self.data)
            self.next_letter_for_data = self.data[-1]
        if first_iteration or socket_type == 'conn': #클라이언트가 첫번째 턴이거나 서버일때
            if socket_type == 'conn':
                timer.start_my_timer(peer_remaining_time, my_socket, socket_type)
            else:
                timer.start_my_timer(15, my_socket, socket_type)
            my_word_entry.config(state='normal')
            my_word_entry_button.config(state='normal')
            my_word_entry_button.config(text='완료')
            my_timer_label.config(bg='#2E64FE')
            my_word_entry.focus_set()
            while not self.my_word_entry_button_clicked: #단어를 적을 때 까지 기다림
                in_game_frm.update()
            self.my_word_entry_button_clicked = False
            rel_word_label.config(text=self.user_word)
            rel_word_label.config(fg='blue')
            word_list_listbox.insert(END,self.user_word)
            word_list_listbox.yview(END)
            word_list_listbox.itemconfig(END, {'fg': 'blue'})
            user_word_info = self.check_word_validity(self.user_word) #플레이어 단어의 정보를 저장
            rel_word_label['text'] = self.user_word
            if not user_word_info['exists']: #플레이어 단어가 존재하지 않을때
                my_socket.sendall(self.user_word.encode())
                my_socket.close()
                result = messagebox.askyesno("패배", f"단어 '{self.user_word}'은/는 존재하지 않습니다.\n다시 하시겠습니까?")
                self.reset_game()
                self.decide_re_game(result,socket_type)
                return True
            elif user_word_info['pos'] != '명사': #플레이어 단어가 명사가 아닐때
                my_socket.sendall(self.user_word.encode())
                my_socket.close()
                result = messagebox.askyesno("패배", f"단어 '{self.user_word}'은/는 명사가 아닙니다.\n다시 하시겠습니까?")
                self.reset_game()
                self.decide_re_game(result,socket_type)
                return True
            if socket_type == 'conn': #서버일때
                if self.user_word[0] != self.next_letter_for_data: #플레이어 단어의 첫글자가 상대의 단어의 마지막 글자와 일치하지 않을때
                    doeum_result = self.is_doeum_applicable(self.user_word,user_word_info,self.next_letter_for_data)
                    if not doeum_result:
                        my_socket.sendall(self.user_word.encode())
                        my_socket.close()
                        result = messagebox.askyesno("패배", f"단어를 잘못 연결했습니다.\n다시 하시겠습니까?")
                        self.reset_game()
                        self.decide_re_game(result,socket_type)
                        return True
                elif self.user_word in self.word_list: #플레이어 단어가 이미 사용한 단어일때
                    my_socket.sendall(self.user_word.encode())
                    my_socket.close()
                    result = messagebox.askyesno("패배", f"단어 '{self.user_word}'은/는 이미 사용되었습니다.\n다시 하시겠습니까?")
                    self.reset_game()
                    self.decide_re_game(result,socket_type)
                    return True
            self.my_remaining_time = timer.get_timer_duration(self.user_word)
            self.word_list.append(self.user_word)
            self.next_letter_for_message = self.user_word[-1]
            my_socket.sendall(self.user_word.encode())
        else: #클라이언트가 첫번째 턴이 아니거나 서버가 아닐때
            timer.start_peer_timer(self.my_remaining_time,my_socket, socket_type)
            try:
                self.data = my_socket.recv(1024).decode() #상대에게 단어를 받음
                timer.set_stop_peer_timer(True)
            except TimeoutError:
                return True
            if not self.data:
                my_socket.close()
                result = messagebox.askyesno("승리", "상대방이 게임을 종료했습니다.\n다시 하시겠습니까?")
                self.reset_game()
                self.decide_re_game(result,socket_type)
                return True
            data_info = self.check_word_validity(self.data) #상대에게 받은 단어의 정보를 저장
            rel_word_label.config(text=self.data)
            rel_word_label.config(fg='black')
            word_list_listbox.insert(END,'    '+str(self.data))
            word_list_listbox.yview(END)
            if not data_info['exists']: #상대의 단어가 존재하지 않을때
                my_socket.close()
                result = messagebox.askyesno("승리", f"상대방의 단어 '{self.data}'은/는 존재하지 않습니다.\n다시 하시겠습니까?")
                self.reset_game()
                self.decide_re_game(result,socket_type)
                return True
            elif data_info['pos'] != '명사': #상대의 단어가 명사가 아닐때
                my_socket.close()
                result = messagebox.askyesno("승리", f"상대방의 단어 '{self.data}'은/는 명사가 아닙니다.\n다시 하시겠습니까?")
                self.reset_game()
                self.decide_re_game(result,socket_type)
                return True
            elif self.data[0] != self.next_letter_for_message:  #상대 단어의 첫글자가 플레이어 단어의 마지막 글자와 일치하지 않을때
                doeum_result = self.is_doeum_applicable(self.data,data_info,self.next_letter_for_message)
                if not doeum_result:
                    my_socket.close()
                    result = messagebox.askyesno("승리", "상대방이 단어를 잘못 연결했습니다.\n다시 하시겠습니까?")
                    self.reset_game()
                    self.decide_re_game(result,socket_type)
                    return True
            elif self.data in self.word_list: #상대 단어가 이미 사용한 단어일때
                my_socket.close()
                result = messagebox.askyesno("승리", f"상대방의 단어 '{self.data}'은/는 이미 사용되었습니다.\n다시 하시겠습니까?")
                self.reset_game()
                self.decide_re_game(result,socket_type)
                return True
            peer_remaining_time = timer.get_timer_duration(self.data)
            self.word_list.append(self.data)
            self.next_letter_for_data = self.data[-1]
            timer.start_my_timer(peer_remaining_time, my_socket, socket_type) 
            my_word_entry.config(state='normal')
            my_word_entry_button.config(state='normal')
            my_word_entry_button.config(text='완료')
            my_timer_label.config(bg='#2E64FE')
            my_word_entry.focus_set()
            while not self.my_word_entry_button_clicked: #단어를 적을 때 까지 기다림
                in_game_frm.update()
            self.my_word_entry_button_clicked = False
            self.next_letter_for_message = self.data[-1]
            user_word_info = self.check_word_validity(self.user_word) #플레이어 단어의 정보를 저장
            rel_word_label.config(text=self.user_word)
            rel_word_label.config(fg='blue')
            word_list_listbox.insert(END,self.user_word)
            word_list_listbox.yview(END)
            word_list_listbox.itemconfig(END, {'fg': 'blue'})
            if not user_word_info['exists']:  #플레이어 단어가 존재하지 않을때
                my_socket.sendall(self.user_word.encode())
                my_socket.close()
                result = messagebox.askyesno("패배", f"단어 '{self.user_word}'은/는 존재하지 않습니다.\n다시 하시겠습니까?")
                self.reset_game()
                self.decide_re_game(result,socket_type)
                return True
            elif user_word_info['pos'] != '명사':  #플레이어 단어가 명사가 아닐때
                my_socket.sendall(self.user_word.encode())
                my_socket.close()
                result = messagebox.askyesno("패배", f"단어 '{self.user_word}'은/는 명사가 아닙니다.\n다시 하시겠습니까?")
                self.reset_game()
                self.decide_re_game(result,socket_type)
                return True
            elif self.user_word[0] != self.next_letter_for_data: #플레이어 단어의 첫글자가 상대의 단어의 마지막 글자와 일치하지 않을때
                doeum_result = self.is_doeum_applicable(self.user_word,user_word_info,self.next_letter_for_data)
                if not doeum_result:
                    my_socket.sendall(self.user_word.encode())
                    my_socket.close()
                    result = messagebox.askyesno("패배", f"단어를 잘못 연결했습니다.\n다시 하시겠습니까?")
                    self.reset_game()
                    self.decide_re_game(result,socket_type)
                    return True
            elif self.user_word in self.word_list: #플레이어의 단어가 이미 사용한 단어일때
                my_socket.sendall(self.user_word.encode())
                my_socket.close()
                result = messagebox.askyesno("패배", f"단어 '{self.user_word}'은/는 이미 사용되었습니다.\n다시 하시겠습니까?")
                self.reset_game()
                self.decide_re_game(result,socket_type)
                return True
            self.my_remaining_time = timer.get_timer_duration(self.user_word)
            self.word_list.append(self.user_word)
            self.next_letter_for_message = self.user_word[-1]
            my_socket.sendall(self.user_word.encode())

class GameConnection:
    def __init__(self, ui, local_ip, port):
        self.ui = ui
        self.local_ip = local_ip
        self.port = port
        self.word_list = []
        self.global_socket = None
        self.next_letter_for_message = ''
        self.next_letter_for_data = ''
    
    def get_global_socket(self):
        return self.global_socket

    #클라이언트 연결을 처리하고 게임을 실행시키는 함수
    def handle_client_connection(self,conn, addr):
        with conn:
            first_iteration = True
            self.word_list = []
            self.next_letter_for_message = ''
            self.next_letter_for_data = ''
            while True: #게임이 끝날때까지 게임을 반복해서 실행
                try:
                    result = game.process_multiplay_turn(first_iteration,'conn', conn)
                    if result:
                        break
                except OSError:
                    break
                first_iteration = False

    def create_server(self):
        HOST = self.local_ip
        PORT = self.port
        #클라이언트의 연결을 기다리는 함수
        def server_thread():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.global_socket = s
                    s.bind((HOST, PORT))
                    s.listen()
                    s.settimeout(10)
                    try: #10초동안 클라이언트의 연결 수락을 기다림
                        conn, addr = s.accept()
                        conn.sendall(b"connected") #연결되면 "connected"를 보냄
                        s.close()
                    except socket.timeout:
                        self.ui.show_prev_frm(connecting_frm,connection_setup_frm,'connecting_prev_button')
                        self.global_socket = None
                        return
                    except OSError:
                        return
                except OSError:
                    return
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #대기중인 클라이언트에 연결
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.global_socket = s
                s.bind((HOST, PORT))
                s.listen()
                conn, addr = s.accept()
            self.ui.show_next_frm(connecting_frm,in_game_frm,'')
            self.handle_client_connection(conn, addr)
        threading.Thread(target=server_thread, daemon=True).start() #UI와 동시에 실행될 수 있게 스레드에서 함수를 실행
        
    def connection_server(self):
        peer_ip = peer_ip_entry.get()
        HOST = peer_ip
        PORT = self.port
        MAX_RETRIES = 5
        rentryy_count = 0
        access = False
        while rentryy_count < MAX_RETRIES: #5번동안 반복
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                self.global_socket = s
                s.settimeout(2)
                try: #2초동안 서버에 연결을 승인받는걸 기다림
                    s.connect((HOST, PORT))
                except TimeoutError:
                    rentryy_count += 1 #2초 안에 연결을 실패하면 연결 기회가 줄어들고 다시 반복
                    continue
                except OSError:
                    return
                s.settimeout(1)
                try:
                    response = s.recv(1024)
                    if response == b"connected": #연결된 서버가 연결하고싶은 올바른 서버인지 확인
                        access = True
                        s.close()
                        break
                    else:
                        rentryy_count += 1 #올바른 서버가 아니라면 연결 기회가 줄어들고 다시 반복
                        continue
                except socket.timeout:
                    pass
        if not access: #연결 기회가 전부 줄어들었을때
            self.ui.show_prev_frm(connecting_frm, connection_setup_frm, 'connecting_prev_button')
            self.global_socket = None
            return
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #올바른 서버에 연결
            s.connect((HOST,PORT))
            self.ui.show_next_frm(connecting_frm, in_game_frm, '')
            Loading.set_stop_connecting_animate(True)
            self.global_socket = None
            first_iteration = True
            self.word_list = []
            self.next_letter_for_message = ''
            self.next_letter_for_data = ''
            while True: #게임이 끝날때까지 게임을 반복해서 실행
                try:
                    result = game.process_multiplay_turn(first_iteration,'s',s)
                    if result:
                        break
                except OSError:
                    break
                first_iteration = False

    #UI와 동시에 실행될 수 있게 스레드에서 함수를 실행
    def start_server_thread(self):
        threading.Thread(target=self.create_server, daemon=True).start()
    def start_client_thread(self):
        threading.Thread(target=self.connection_server, daemon=True).start()

class Timer:
    def __init__(self,game):
        self.game = game
        self.stop_my_timer = False
        self.stop_peer_timer = False
        self.stop_singleplayer_timer = False
        self.peer_remaining_time = 0
    
    def set_stop_my_timer(self, value):
        self.stop_my_timer = value
        
    def set_stop_peer_timer(self, value):
        self.stop_peer_timer = value
        
    def set_stop_singleplay_timer(self, value):
        self.stop_singleplayer_timer = value
    
    #단어의 길이에 따라 제한시간을 정하는 함수
    def get_timer_duration(self,word):
        word_length = len(word)
        if word_length <= 3:
            return 15
        elif word_length <= 5:
            return 10
        else:
            return 7
    
    #플레이어의 타이머를 실행하는 함수
    def start_my_timer(self,duration, my_socket, socket_type):
        self.stop_my_timer = False
        start_time = time.time()
        my_timer_bar_length = 276/duration
        def check_my_time():
            if self.stop_my_timer: #타이머를 멈추는 함수가 True라면 멈추기
                return
            elapsed_time = time.time() - start_time
            remaining_time = duration - elapsed_time
            my_timer_bar.config(text=round(remaining_time, 1))
            if remaining_time <= 0: #제한시간이 끝났을때
                my_timer_bar.place(x=82,y=267,width=0,height=15)
                my_socket.close()
                result = messagebox.askyesno("패배", "입력시간이 초과되었습니다.\n다시 하시겠습니까?")
                self.game.reset_game()
                self.game.decide_re_game(result, socket_type)
                return
            else:
                current_bar_length = my_timer_bar_length * remaining_time
                my_timer_bar.place(x=82,y=267,width=current_bar_length,height=15)
                window.after(100,check_my_time) #0.1초 후에 재귀 호출
        check_my_time()

    #싱글플레이어의 타이머를 실행하는 함수
    def start_singleplayer_timer(self,duration):
        self.stop_singleplayer_timer = False
        start_time = time.time()
        my_timer_bar_length = 276/duration
        self.timer_ids = []
        def check_my_time():
            elapsed_time = time.time() - start_time
            remaining_time = duration - elapsed_time
            my_timer_bar.config(text=round(remaining_time, 1))
            if remaining_time <= 0: #제한시간이 끝났을때
                my_timer_bar.place(x=82,y=267,width=0,height=15)
                result = messagebox.askyesno("패배", "입력시간이 초과되었습니다.\n다시 하시겠습니까?")
                self.game.reset_game()
                self.game.decide_re_game(result,'')
                return
            else:
                current_bar_length = my_timer_bar_length * remaining_time
                my_timer_bar.place(x=82,y=267,width=current_bar_length,height=15)
                if not self.stop_singleplayer_timer:
                    window.after(100, check_my_time) #0.1초 후에 재귀 호출
                else:
                    return
        check_my_time()

    #상대의 타이머를 실행하는 함수
    def start_peer_timer(self,duration, my_socket, socket_type):
        self.stop_peer_timer = False
        start_time = time.time()
        def check_peer_time():
            if self.stop_peer_timer: #타이머를 멈추는 함수가 True라면 멈추기
                return
            elapsed_time = time.time() - start_time
            remaining_time = duration - elapsed_time
            if remaining_time <= 0: #제한시간이 끝났을때
                my_socket.close()
                result = messagebox.askyesno("승리", f"상대방의 입력시간이 초과되었습니다.\n다시 하시겠습니까?")
                self.game.reset_game()
                self.game.decide_re_game(result, socket_type)
                return True
            else:
                window.after(100, check_peer_time) #0.1초 후에 재귀 호출
        check_peer_time()

class UI:
    def __init__(self):
        self.current_role = ''
        self.current_index = 1
    
    def get_current_role(self):
        return self.current_role
    
    def get_current_index(self):
        return self.current_index

    #다음 프레임으로 넘기는 함수
    def show_next_frm(self,current_frm,next_frm,button_name):
        current_frm.place_forget()
        next_frm.place(x=0,y=0,width=600,height=400)
        if button_name == 'creat_server':
            self.current_role = 'server'
        elif button_name == 'access_server':
            peer_ip_entry_button.place(x=364,y=336,width=34,height=28)
            peer_ip_entry_button_label.place(x=363,y=335,width=36,height=30)
            peer_ip_entry.place(x=201, y=335, width=162, height=30)
            self.current_role = 'client'
        elif button_name == 'multiplay_start_button':
            connecting_label.config(text='')
            Loading.set_stop_connecting_animate(False)
            Loading.connecting_animate()
        elif button_name == 'singleplay_start_button':
            loading_label.config(text='')
            Loading.set_stop_loading_animate(False)
            Loading.loading_animate()
        elif button_name == 'singleplay':
            singleplay()

    #이전 프레임으로 넘기는 함수
    def show_prev_frm(self,current_frm,prev_frm,button_name):
        current_frm.place_forget()
        prev_frm.place(x=0,y=0,width=600,height=400)
        try:
            global_socket = game_connection.get_global_socket()
            if global_socket:
                global_socket.close()
                global_socket = None
        except NameError:
            pass
        except OSError:
            pass
        if button_name == 'setup_prev_button':
            self.current_role = ''
            peer_ip_entry_button.place_forget()
            peer_ip_entry_button_label.place_forget()
            peer_ip_entry.place_forget()
        elif button_name == 'connecting_prev_button':
            Loading.set_stop_connecting_animate(True)
        elif button_name == 'loading_prev_button':
            Loading.set_stop_loading_animate(True)
            
    #난이도를 변경하는 함수
    def change_label(self,direction):
        if direction == "left" and self.current_index > 0:
            self.current_index -= 1
            right_button.config(state='normal')
            if self.current_index == 0:
                left_button.config(state='disabled')
        elif direction == "right" and self.current_index < 2:
            self.current_index += 1
            left_button.config(state='normal')
            if self.current_index == 2:
                right_button.config(state='disabled')
        difficulty_label.config(text=difficulty_levels[self.current_index])

class Loading:
    def __init__(self):
        self.stop_connecting_animate = False
        self.stop_loading_animate = False
    
    def set_stop_connecting_animate(self, value):
        self.stop_connecting_animate = value
    
    def set_stop_loading_animate(self, value):
        self.stop_loading_animate = value

    #연결화면을 구현하는 함수
    def connecting_animate(self,index=0):
        text = "연결하는 중..."
        if not self.stop_connecting_animate:
            if index < len(text):
                connecting_label.config(text=text[:index+1])
                connecting_label.after(200, self.connecting_animate, index + 1)
            else:
                connecting_label.after(200, self.connecting_animate)
                connecting_label.config(text='')
        else:
            return
    
    #로딩화면을 구현하는 함수
    def loading_animate(self, index=0, repeat=1):
        text = "로딩 중..."
        if repeat > 0 and not self.stop_loading_animate:
            if index < len(text):
                loading_label.config(text=text[:index + 1])
                loading_label.after(200, self.loading_animate, index + 1, repeat)
            else:
                loading_label.after(200, self.loading_animate, 0, repeat - 1)
        elif repeat == 0:
            ui.show_next_frm(loading_frm,in_game_frm,'singleplay')
            return
        else:
            return

class IPAddressValidator:
    def __init__(self):
        self.peer_ip = ''
        self.local_ip = local_ip

    #상대의 로컬 IP가 올바른지 확인하는 함수
    def is_valid_ipv4(self):
        peer_ip = peer_ip_entry.get()
        try:
            if not peer_ip: #아무것도 입력하지 않았을때
                peer_ip_entry.config(state='normal')
                peer_ip_entry.delete(0, END)
                peer_ip_entry.insert(0, "상대 아이피 입력")
                peer_ip_entry_button.config(text='입력')
                peer_ip_entry.config(state='disable',justify='center')
            elif peer_ip == local_ip: #플레이어의 로컬 IP와 같을때
                peer_ip_entry.config(state='normal')
                peer_ip_entry.delete(0, END)
                peer_ip_entry.insert(0, "상대 아이피 입력")
                peer_ip_entry_button.config(text='입력')
                peer_ip_entry.config(state='disable',justify='center')
                messagebox.showerror("IP 오류", "자신의 IP를 입력할 수 없습니다.")
            else:
                ipaddress.IPv4Address(peer_ip)
                peer_ip_entry_button.config(text='입력')
                peer_ip_entry.config(state='disable',justify='center')
        except ipaddress.AddressValueError: #올바르지 않은 IP 형식일때
            peer_ip_entry.config(state='normal')
            peer_ip_entry.delete(0, END)
            peer_ip_entry.insert(0, "상대 아이피 입력")
            peer_ip_entry_button.config(text='입력')
            peer_ip_entry.config(state='disable',justify='center')
            messagebox.showerror("IP 오류", "잘못된 로컬 IP 주소입니다.")
    
    #플레이어의 로컬 IP를 클립보드에 복사하는 함수
    def copy_local_ip(self,local_ip):
        try:
            current_clipboard = window.clipboard_get()
        except:
            current_clipboard = ""

        if current_clipboard != local_ip:
            window.clipboard_clear()
            window.clipboard_append(local_ip)
        my_ip_label_button.config(text="복사됨")
        my_ip_label_button.config(state="disabled")
        window.after(1000, lambda: my_ip_label_button.config(text="복사",state="normal"))

    #상대 로컬 IP를 적는 엔트리를 활성화 하는 함수
    def enable_peer_ip_entry(self):
        peer_ip_entry.config(state='normal',justify='left')
        if peer_ip_entry.get() == '상대 아이피 입력':
            peer_ip_entry.delete(0, END)

    def toggle_peer_ip(self,event=None):
        if peer_ip_entry['state'] == 'normal':
            self.is_valid_ipv4()
        else:
            peer_ip_entry_button.config(text='완료')
            self.enable_peer_ip_entry()

class PortChecker:
    def __init__(self):
        self.port = None
    
    #포트번호가 올바른지 확인하는 함수
    def is_valid_port(self):
        port = port_entry.get().strip()
        try:
            port = int(port)
            if not 1024 <= port <= 49151: #포트번호가 사용할 수 있는 번호가 아닐때
                port_entry.config(state='normal')
                port_entry.delete(0, END)
                port_entry.insert(0, "포트 입력")
                port_entry_button.config(text='입력')
                port_entry.config(state='disabled', justify='center')
                messagebox.showerror("포트 오류", "사용할 수 없는 포트번호 입니다.")
                return False
            #포트번호의 사용 여부를 확인하는 코드
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                if sock.connect_ex(('localhost', port)) == 0:
                    port_entry.config(state='normal')
                    port_entry.delete(0, END)
                    port_entry.insert(0, "포트 입력")
                    port_entry_button.config(text='입력')
                    port_entry.config(state='disabled', justify='center')
                    messagebox.showerror("포트 오류", "이미 사용중인 포트번호 입니다.")
                    return False
                else:
                    port_entry.config(state='normal')
                    port_entry_button.config(text='입력')
                    port_entry.config(state='disabled', justify='center')
                    return True

        except ValueError:
            if not port: #아무것도 입력하지 않았을때
                port_entry.config(state='normal')
                port_entry.delete(0, END)
                port_entry.insert(0, "포트 입력")
                port_entry_button.config(text='입력')
                port_entry.config(state='disabled', justify='center')
                return False
            else:
                port_entry.config(state='normal')
                port_entry.delete(0, END)
                port_entry.insert(0, "포트 입력")
                port_entry_button.config(text='입력')
                port_entry.config(state='disabled', justify='center')
                messagebox.showerror("포트 오류", "포트번호는 숫자여야 합니다.")
                return False

    #UI와 동시에 실행될 수 있게 스레드에서 함수를 실행
    def port_thread(self):
        threading.Thread(target=self.is_valid_port).start()

    #포트를 적는 엔트리를 활성화 하는 함수
    def enable_port_entry(self):
        port_entry.config(state='normal',justify='left')
        if port_entry.get() == '포트 입력':
            port_entry.delete(0, END)

    def toggle_port(self,event=None):
        if port_entry['state'] == 'normal':
            self.is_valid_port()
        else:
            port_entry_button.config(text='완료')
            self.enable_port_entry()

#메서드를 사용할 수 있게 변수로 저장
ui = UI()
game = Game(ui)
timer = Timer(game)
Loading = Loading()
ip_validator = IPAddressValidator()
port_checker = PortChecker()

def singleplay():
    def handle_singleplay(first_iteration):
        result = game.singleplay_player(first_iteration)
        if result:
            return
        elif result == False:
            handle_singleplay(False)
    handle_singleplay(True)

#개암울 사적하기 전 포트와 로컬 IP를 확인하는 함수
def valid_entry_before_start():
    global game_connection
    port = port_entry.get()
    if ui.get_current_role() == 'client': #클라이언트일때
        if peer_ip_entry['state'] == 'disabled' and port_entry['state'] == 'disabled': #모든 엔트리가 비활성화일때
            peer_ip = peer_ip_entry.get()
            if peer_ip == '상대 아이피 입력' and port == '포트 입력': #엔트리를 건들이지 않았을때
                messagebox.showerror("입력 오류","아이피와 포트를 입력해주세요.")
            elif peer_ip == '상대 아이피 입력': #IP 엔트리만 건들이지 않았을때
                messagebox.showerror("입력 오류","아이피를 입력해주세요.")
            elif port == '포트 입력': #포트 엔트리만 건들이지 않았을때
                messagebox.showerror("입력 오류","포트를 입력해주세요.")
            else:
                ui.show_next_frm(connection_setup_frm,connecting_frm,'multiplay_start_button')
                Loading.set_stop_connecting_animate(False)
                Loading.connecting_animate()
                game_connection = GameConnection(ui, local_ip, int(port))
                game.set_global_socket()
                game_connection.start_client_thread()
        else:
            messagebox.showerror("입력 오류","입력을 완료해주세요.")
    else: #서버일때
        if port_entry['state'] == 'disabled': #엔트리가 비활성화일때
            if port == '포트 입력': #엔트리를 건들이지 않았을때
                messagebox.showerror("입력 오류","포트를 입력해주세요.")
            else:
                ui.show_next_frm(connection_setup_frm,connecting_frm,'multiplay_start_button')
                Loading.set_stop_connecting_animate(False)
                Loading.connecting_animate()
                game_connection = GameConnection(ui, local_ip, int(port))
                game.set_global_socket()
                game_connection.start_server_thread()
        else:
            messagebox.showerror("입력 오류","입력을 완료해주세요.")

def call_functions(event):
    if peer_ip_entry['state'] == 'normal' and port_entry['state'] == 'normal':
        port_checker.is_valid_port()
        ip_validator.is_valid_ipv4()
    elif peer_ip_entry['state'] == 'normal':
        ip_validator.is_valid_ipv4()
    elif port_entry['state'] == 'normal':
        port_checker.is_valid_port()

#게임 타이틀 UI를 만드는 함수
def create_bordered_text(canvas, x, y, text, font, text_color, border_color, border_width):
    for offset_x in range(-border_width, border_width + 1):
        for offset_y in range(-border_width, border_width + 1):
            if offset_x != 0 or offset_y != 0:
                canvas.create_text(x + offset_x, y + offset_y, text=text, font=font, fill=border_color)
    canvas.create_text(x, y, text=text, font=font, fill=text_color)
#=====================================================================윈도우 생성====================================================================#
window = Tk()
window.title("끝말잇기 프로그램")
window.geometry('600x400')
window['bg'] = '#FFFFFF'
window.resizable(False, False)
#===================================================================기본 프레임 생성===================================================================#
main_menu_frm = Frame(window)
main_menu_frm['bg'] = '#FFFFFF'
main_menu_frm.place(x=0,y=0,width=600,height=400)

select_difficulty_frm = Frame(window)
select_difficulty_frm['bg'] = '#FFFFFF'

multiplay_frm = Frame(window)
multiplay_frm['bg'] = '#FFFFFF'

connection_setup_frm = Frame(window)
connection_setup_frm['bg'] = '#FFFFFF'

loading_frm = Frame(window)
loading_frm['bg'] = '#FFFFFF'

connecting_frm = Frame(window)
connecting_frm['bg'] = '#FFFFFF'

in_game_frm = Frame(window)
in_game_frm['bg'] = '#FFFFFF'
#=====================================================================main_menu_frm=====================================================================#
canvas = Canvas(main_menu_frm,relief='flat',highlightthickness=0)
canvas.place(x=0,y=60,width=600,height=120)
canvas['bg'] = main_menu_frm['bg']
text = "끝말 잇기"
title_font = ("ONE Mobile POP", 60)
text_color = '#FFFFFF'
border_color = '#000000'
border_width = 8

create_bordered_text(canvas, 300, 60, text, title_font, text_color, border_color, border_width)

button_border_1 = Label(main_menu_frm,relief='flat')
button_border_1.place(x=90,y=220,width=420,height=50)
button_border_1['bg'] = '#000000'

button_border_2 = Label(main_menu_frm,relief='flat')
button_border_2.place(x=90,y=295,width=420,height=50)
button_border_2['bg'] = '#000000'

singleplay_button = Button(main_menu_frm,relief='flat',command=lambda: ui.show_next_frm(main_menu_frm,select_difficulty_frm,'singleplay_button'),font=("ONE Mobile POP", 30))
singleplay_button.place(x=95,y=225,width=410,height=40)
singleplay_button['text'] = '싱글플레이'
singleplay_button['fg'] = '#000000'
singleplay_button['bg'] = '#FFFFFF'

multiplay_button = Button(main_menu_frm,relief='flat',command=lambda: ui.show_next_frm(main_menu_frm,multiplay_frm,'access_server'),font=("ONE Mobile POP", 30))
multiplay_button.place(x=95,y=300,width=410,height=40)
multiplay_button['text'] = '멀티플레이'
multiplay_button['fg'] = '#000000'
multiplay_button['bg'] = '#FFFFFF'
#==================================================================select_difficulty_frm===============================================================#
difficulty_levels = ["쉬움", "보통", "어려움"]

canvas = Canvas(select_difficulty_frm,relief='flat',highlightthickness=0)
canvas.place(x=0,y=60,width=600,height=120)
canvas['bg'] = select_difficulty_frm['bg']
text = "끝말 잇기"
title_font = ("ONE Mobile POP", 60)
text_color = '#FFFFFF'
border_color = '#000000'
border_width = 8

create_bordered_text(canvas, 300, 60, text, title_font, text_color, border_color, border_width)

difficulty_label = Label(select_difficulty_frm, text=difficulty_levels[ui.current_index], font=("ONE Mobile POP", 25),relief='solid', bd=4)
difficulty_label['bg'] = '#FFFFFF'
difficulty_label.place(x=225, y=240, width=150, height=60)

left_button = Button(select_difficulty_frm, text="◁", command=lambda: ui.change_label("left"), font=("ONE Mobile POP", 25),relief='flat')
left_button['bg'] = '#FFFFFF'
left_button.place(x=185, y=250, width=40, height=40)

right_button = Button(select_difficulty_frm, text="▷", command=lambda: ui.change_label("right"), font=("ONE Mobile POP", 25),relief='flat')
right_button['bg'] = '#FFFFFF'
right_button.place(x=375, y=250, width=40, height=40)

singleplay_start_button = Button(select_difficulty_frm,relief='ridge',command=lambda: ui.show_next_frm(select_difficulty_frm,loading_frm,'singleplay_start_button'),font=("ONE Mobile POP",22))
singleplay_start_button.place(x=530,y=355,width=65,height=40)
singleplay_start_button['text'] = '시작'
singleplay_start_button['bg'] = '#088A08'
singleplay_start_button['fg'] = '#FFFFFF'

prev_button = Button(select_difficulty_frm,relief='flat',command=lambda: ui.show_prev_frm(select_difficulty_frm,main_menu_frm,'prev_button'),font=("ONE Mobile POP",18))
prev_button.place(x=5,y=358,width=90,height=33)
prev_button['text'] = '◁ 이전'
prev_button['bg'] = '#FFFFFF'
#====================================================================multiplay_frm======================================================================#
canvas = Canvas(multiplay_frm,relief='flat',highlightthickness=0)
canvas.place(x=0,y=60,width=600,height=120)
canvas['bg'] = multiplay_frm['bg']
text = "끝말 잇기"
title_font = ("ONE Mobile POP", 60)
text_color = '#FFFFFF'
border_color = '#000000'
border_width = 8

create_bordered_text(canvas, 300, 60, text, title_font, text_color, border_color, border_width)

button_border_1 = Label(multiplay_frm,relief='flat')
button_border_1.place(x=90,y=220,width=420,height=50)
button_border_1['bg'] = '#000000'

button_border_2 = Label(multiplay_frm,relief='flat')
button_border_2.place(x=120,y=295,width=360,height=50)
button_border_2['bg'] = '#000000'

create_server_button = Button(multiplay_frm,relief='flat',command=lambda: ui.show_next_frm(multiplay_frm,connection_setup_frm,'create_server'),font=("ONE Mobile POP", 30))
create_server_button.place(x=95,y=225,width=410,height=40)
create_server_button['text'] = '서버 생성하기'
create_server_button['fg'] = '#000000'
create_server_button['bg'] = '#FFFFFF'

access_server_button = Button(multiplay_frm,relief='flat',command=lambda: ui.show_next_frm(multiplay_frm,connection_setup_frm,'access_server'),font=("ONE Mobile POP", 30))
access_server_button.place(x=125,y=300,width=350,height=40)
access_server_button['text'] = '서버 접속하기'
access_server_button['fg'] = '#000000'
access_server_button['bg'] = '#FFFFFF'

multiplay_prev_button = Button(multiplay_frm,relief='flat',command=lambda: ui.show_prev_frm(multiplay_frm,main_menu_frm,'setup_prev_button'),font=("ONE Mobile POP",18))
multiplay_prev_button.place(x=5,y=358,width=90,height=33)
multiplay_prev_button['text'] = '◁ 이전'
multiplay_prev_button['bg'] = '#FFFFFF'
#=====================================================================connection_setup_frm=====================================================================#
setup_canvas = Canvas(connection_setup_frm,relief='flat',highlightthickness=0)
setup_canvas.place(x=0,y=60,width=600,height=120)
setup_canvas['bg'] = multiplay_frm['bg']
text = "끝말 잇기"
title_font = ("ONE Mobile POP", 60)
text_color = '#FFFFFF'
border_color = '#000000'
border_width = 8

create_bordered_text(setup_canvas, 300, 60, text, title_font, text_color, border_color, border_width)

my_ip_label = Label(connection_setup_frm,anchor='w',font=("ONE Mobile POP",15))
my_ip_label.place(x=195,y=225,width=230,height=30)
my_ip_label['text'] = local_ip

my_ip_label_button = Button(connection_setup_frm,command=lambda: ip_validator.copy_local_ip(local_ip),font=("ONE Mobile POP",15))
my_ip_label_button.place(x=362,y=228,width=60,height=24)
my_ip_label_button['text'] = '복사'

peer_ip_entry = Entry(connection_setup_frm,validate="key",font=("ONE Mobile POP",15),justify='center')
peer_ip_entry.insert(0, '상대 아이피 입력')
peer_ip_entry['bg'] = '#FFFFFF'
peer_ip_entry['fg'] = '#0040FF'
peer_ip_entry['state'] = 'disabled'

peer_ip_entry_button_label = Label(connection_setup_frm,relief='flat')
peer_ip_entry_button_label['bg'] = '#000000'

peer_ip_entry_button = Button(connection_setup_frm,relief='flat',command=ip_validator.toggle_peer_ip,font=("ONE Mobile POP",14))
peer_ip_entry_button['text'] = '입력'
peer_ip_entry_button['bg'] = '#FFFFFF'
peer_ip_entry_button['fg'] = '#000000'

port_entry = Entry(connection_setup_frm,validate="key",font=("ONE Mobile POP",15),justify='center')
port_entry.place(x=223,y=280,width=120,height=30)
port_entry.insert(0, '포트 입력')
port_entry['bg'] = '#FFFFFF'
port_entry['fg'] = '#0040FF'
port_entry['state'] = 'disabled'

port_entry_button_label = Label(connection_setup_frm,relief='flat')
port_entry_button_label.place(x=344,y=280,width=34,height=30)
port_entry_button_label['bg'] = '#000000'

port_entry_button = Button(connection_setup_frm,relief='flat',command=port_checker.toggle_port,font=("ONE Mobile POP",14))
port_entry_button.place(x=345,y=281,width=32,height=28)
port_entry_button['text'] = '입력'
port_entry_button['bg'] = '#FFFFFF'
port_entry_button['fg'] = '#000000'

setup_prev_button = Button(connection_setup_frm,relief='flat',command=lambda: ui.show_prev_frm(connection_setup_frm,multiplay_frm,'setup_prev_button'),font=("ONE Mobile POP",18))
setup_prev_button.place(x=5,y=358,width=90,height=33)
setup_prev_button['text'] = '◁ 이전'
setup_prev_button['bg'] = '#FFFFFF'

multiplay_start_button = Button(connection_setup_frm,relief='ridge',command=lambda: valid_entry_before_start(),font=("ONE Mobile POP",22))
multiplay_start_button.place(x=530,y=355,width=65,height=40)
multiplay_start_button['text'] = '시작'
multiplay_start_button['bg'] = '#088A08'
multiplay_start_button['fg'] = '#FFFFFF'

connection_setup_frm.bind("<Button-1>", call_functions)
setup_canvas.bind("<Button-1>", call_functions)
#=======================================================================loading_frm=======================================================================#
loading_label = Label(loading_frm,text="",font=("ONE Mobile POP", 40),justify='center')
loading_label['bg'] = '#FFFFFF'
loading_label.place(x=150,y=145,width=300,height=60)

loading_prev_button = Button(loading_frm,relief='ridge',command=lambda: ui.show_prev_frm(loading_frm,select_difficulty_frm,'loading_prev_button'),font=("ONE Mobile POP", 20))
loading_prev_button.place(x=270,y=255,width=60,height=40)
loading_prev_button['text'] = '취소'
loading_prev_button['bg'] = '#DF0101'
loading_prev_button['fg'] = '#FFFFFF'
#=====================================================================connecting_frm=======================================================================#
connecting_label = Label(connecting_frm,text="",font=("ONE Mobile POP", 40),justify='center')
connecting_label['bg'] = '#FFFFFF'
connecting_label.place(x=150,y=145,width=300,height=60)

connecting_prev_button = Button(connecting_frm,relief='ridge',command=lambda: ui.show_prev_frm(connecting_frm,connection_setup_frm,'connecting_prev_button'),font=("ONE Mobile POP", 20))
connecting_prev_button.place(x=270,y=255,width=60,height=40)
connecting_prev_button['text'] = '취소'
connecting_prev_button['bg'] = '#DF0101'
connecting_prev_button['fg'] = '#FFFFFF'
#=====================================================================in_game_frm=====================================================================#
rel_word_label_outline = Label(in_game_frm,relief='flat')
rel_word_label_outline.place(x=60,y=50,width=280,height=170)
rel_word_label_outline['bg'] = '#000000'

rel_word_label = Label(in_game_frm,relief='flat',font=("ONE Mobile POP", 25),justify='center')
rel_word_label.place(x=62,y=52,width=276,height=166)
rel_word_label['bg'] = '#FFFFFF'
rel_word_label['fg'] = '#000000'

my_timer_label = Label(in_game_frm,relief='flat')
my_timer_label.place(x=80,y=265,width=280,height=19)
my_timer_label['bg'] = '#D8D8D8'

my_timer_bar = Label(in_game_frm,relief='flat',font=("ONE Mobile POP", 12))
my_timer_bar.place(x=82,y=267,width=276,height=15)
my_timer_bar['text'] = '10'
my_timer_bar['bg'] = '#A9BCF5'

my_word_entry = Entry(in_game_frm,font=("ONE Mobile POP", 15))
my_word_entry.place(x=80,y=284,width=240,height=30)
my_word_entry['state'] = 'disabled'

my_word_entry_button = Button(in_game_frm,relief='ridge',command=game.disable_my_word_entry,font=("ONE Mobile POP", 15))
my_word_entry_button.place(x=320,y=284,width=40,height=30)
my_word_entry_button['text'] = '완료'
my_word_entry_button['state'] = 'disabled'

my_word_entry.bind('<Return>', lambda event: game.disable_my_word_entry())

word_list_listbox = Listbox(in_game_frm,relief='flat',font=("ONE Mobile POP", 15))
word_list_listbox.place(x=400,y=60,width=120,height=240)

word_list_listbox_scrollbar = Scrollbar(in_game_frm,orient="v",command=word_list_listbox.yview)
word_list_listbox_scrollbar.place(x=520,y=60,width=10,height=240)

word_list_listbox.configure(yscrollcommand=word_list_listbox_scrollbar.set)

#========================================================================메인루프 실행====================================================================#
window.mainloop()