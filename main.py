import streamlit as st
import pandas as pd
import random
import os
import time

# --- ページ設定 ---
st.set_page_config(page_title="英検2級 合格特訓 PRO", layout="centered")

# --- データ読み込み（最強版） ---
def load_data(filename):
    file_path = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.exists(file_path):
        return []
    
    # 試す文字コードのリスト
    encodings = ["utf-8", "shift-jis", "utf-8-sig", "cp932"]
    
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                data = []
                for line in f:
                    line = line.strip()
                    if "," in line:
                        parts = line.split(",")
                        # load_data関数の中身をこのように修正
if "," in line:
    parts = line.split(",")
    if len(parts) >= 2:
        # .strip() を追加することで、前後の余計な空白や改行をすべて除去します
        word = parts[0].strip()
        meaning = parts[1].strip()
        
        if word != "" and meaning != "":
            data.append((word, meaning))
                
                if data: # 読み込めたら結果を返す
                    return data
        except:
            continue
            
    st.error(f"{filename} の読み込みに失敗しました。ファイルの中身が「単語,意味」の形式になっているか確認してください。")
    return []

# --- セッション状態の初期化 ---
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = []
    st.session_state.current_idx = 0
    st.session_state.score = 0
    st.session_state.options = []
    st.session_state.is_answered = False
    st.session_state.quiz_active = False
    st.session_state.start_time = 0

# --- 📱 メニュー機能（サイドバー） ---
with st.sidebar:
    st.header("⚙️ メニュー")
    mode = st.radio("学習項目", ["英単語", "英熟語"])
    num_q = st.slider("問題数", 5, 50, 10)
    st.divider()
    st.write("制作: izu640412")
    if st.button("データをリセット"):
        st.session_state.quiz_active = False
        st.rerun()

# --- メイン画面 ---
st.title("📚 英検2級 合格特訓 Web")

if not st.session_state.quiz_active:
    if st.button("クイズを開始する", use_container_width=True):
        filename = "wordlist.txt" if mode == "英単語" else "idiomlist.txt"
        data = load_data(filename)
        if data:
            st.session_state.quiz_data = random.sample(data, min(len(data), num_q))
            st.session_state.current_idx = 0
            st.session_state.score = 0
            st.session_state.quiz_active = True
            st.session_state.is_answered = False
            st.session_state.start_time = time.time() # タイマー開始
            st.rerun()

if st.session_state.quiz_active:
    q_list = st.session_state.quiz_data
    idx = st.session_state.current_idx
    
    if idx < len(q_list):
        word, correct_meaning = q_list[idx]
        
        # ⏱️ タイマー表示
        elapsed_time = int(time.time() - st.session_state.start_time)
        st.write(f"⏱️ 経過時間: {elapsed_time}秒")

        st.subheader(f"第 {idx + 1} 問 / {len(q_list)}")
        st.info(f"### {word}")

        if not st.session_state.options:
            others = [m for w, m in q_list if m != correct_meaning]
            st.session_state.options = random.sample(others, min(len(others), 3)) + [correct_meaning]
            random.shuffle(st.session_state.options)

        # 4択ボタン
        for opt in st.session_state.options:
            if st.button(opt, use_container_width=True, disabled=st.session_state.is_answered):
                st.session_state.is_answered = True
                if opt == correct_meaning:
                    st.session_state.score += 1
                    st.success("⭕ 正解！")
                else:
                    st.error(f"❌ 残念！正解は: {correct_meaning}")
                
                if st.button("次へ"):
                    st.session_state.current_idx += 1
                    st.session_state.is_answered = False
                    st.session_state.options = []
                    st.rerun()
    else:
        # 結果発表
        st.balloons()
        total_time = int(time.time() - st.session_state.start_time)
        st.header("🎉 クイズ終了！")
        st.subheader(f"スコア: {st.session_state.score} / {len(q_list)}")
        st.write(f"⏱️ かかった時間: {total_time}秒")
        if st.button("もう一度挑戦"):
            st.session_state.quiz_active = False
            st.rerun()
