import streamlit as st
import pandas as pd
import random
import os
import time

# --- ページ設定 ---
st.set_page_config(page_title="英検2級 合格特訓 PRO", layout="centered")

# --- データ読み込み（最強・空白対策版） ---
def load_data(filename):
    file_path = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.exists(file_path):
        return []
    
    encodings = ["utf-8", "shift-jis", "utf-8-sig", "cp932"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                data = []
                for line in f:
                    line = line.strip()
                    if "," in line:
                        parts = line.split(",")
                        if len(parts) >= 2:
                            # 前後の余計な空白を完全に除去
                            word = parts[0].strip()
                            meaning = parts[1].strip()
                            if word != "" and meaning != "":
                                data.append((word, meaning))
                if data:
                    return data
        except:
            continue
    return []

# --- セッション状態の初期化 ---
if 'all_data' not in st.session_state:
    st.session_state.all_data = []
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = []
    st.session_state.current_idx = 0
    st.session_state.score = 0
    st.session_state.options = []
    st.session_state.is_answered = False
    st.session_state.quiz_active = False
    st.session_state.start_time = 0
    st.session_state.feedback = ""

# --- メニュー（サイドバー） ---
with st.sidebar:
    st.header("⚙️ メニュー")
    mode = st.radio("学習項目", ["英単語", "英熟語"])
    num_q = st.slider("問題数", 5, 50, 10)
    st.divider()
    if st.button("リセットしてTOPへ"):
        st.session_state.quiz_active = False
        st.rerun()

# --- メイン画面 ---
st.title("📚 英検2級 合格特訓 Web")

if not st.session_state.quiz_active:
    if st.button("クイズを開始する", use_container_width=True):
        filename = "wordlist.txt" if mode == "英単語" else "idiomlist.txt"
        data = load_data(filename)
        if data:
            st.session_state.all_data = data # 全データを保持
            st.session_state.quiz_data = random.sample(data, min(len(data), num_q))
            st.session_state.current_idx = 0
            st.session_state.score = 0
            st.session_state.quiz_active = True
            st.session_state.is_answered = False
            st.session_state.start_time = time.time()
            st.rerun()
        else:
            st.error("データの読み込みに失敗しました。ファイル名や中身を確認してください。")

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

        # --- 選択肢の作成ロジック（全データからハズレを抽出） ---
        if not st.session_state.options:
            # 1. 確実に正解をリストに入れる
            options = [correct_meaning]
            # 2. 全データから「正解以外の意味」をランダムに3つ選ぶ
            all_meanings = list(set([m for w, m in st.session_state.all_data if m != correct_meaning]))
            if len(all_meanings) >= 3:
                wrong_options = random.sample(all_meanings, 3)
                options.extend(wrong_options)
            else:
                options.extend(["---", "---", "---"])
            # 3. シャッフル
            random.shuffle(options)
            st.session_state.options = options

        # --- 回答エリア ---
        if not st.session_state.is_answered:
            for opt in st.session_state.options:
                if st.button(opt, use_container_width=True):
                    st.session_state.is_answered = True
                    if opt == correct_meaning:
                        st.session_state.score += 1
                        st.session_state.feedback = "⭕ 正解！"
                    else:
                        st.session_state.feedback = f"❌ 残念！正解は: {correct_meaning}"
                    st.rerun()
        else:
            # 回答後のフィードバック表示
            if "⭕" in st.session_state.feedback:
                st.success(st.session_state.feedback)
            else:
                st.error(st.session_state.feedback)
            
            if st.button("次の問題へ ➡️", use_container_width=True):
                st.session_state.current_idx += 1
                st.session_state.is_answered = False
                st.session_state.options = []
                st.rerun()
    else:
        # --- 結果発表 ---
        st.balloons()
        total_time = int(time.time() - st.session_state.start_time)
        st.header("🎉 クイズ終了！ お疲れ様でした")
        st.metric("あなたのスコア", f"{st.session_state.score} / {len(q_list)}")
        st.write(f"⏱️ 合計時間: {total_time}秒")
        
        if st.button("トップに戻る", use_container_width=True):
            st.session_state.quiz_active = False
            st.rerun()
