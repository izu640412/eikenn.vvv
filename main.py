import streamlit as st
import pandas as pd
import random
import os

# --- ページの設定（スマホで見やすくする） ---
st.set_page_config(page_title="英検2級 合格特訓 Web", layout="centered")

# --- データの読み込み関数 ---
def load_data(filename):
    # GitHub上のファイルパスを取得
    file_path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(file_path):
        try:
            # Shift-JISかUTF-8か自動で対応できるように読み込み
            with open(file_path, "r", encoding="utf-8") as f:
                data = [line.strip().split(",") for line in f if "," in line]
            return [(d[0].strip(), d[1].strip()) for d in data]
        except:
            with open(file_path, "r", encoding="shift-jis") as f:
                data = [line.strip().split(",") for line in f if "," in line]
            return [(d[0].strip(), d[1].strip()) for d in data]
    return []

# --- セッション状態の初期化（Webアプリで値を保持する仕組み） ---
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = []
    st.session_state.current_idx = 0
    st.session_state.score = 0
    st.session_state.options = []
    st.session_state.is_answered = False
    st.session_state.quiz_active = False
    st.session_state.feedback = ""

# --- メイン画面の表示 ---
st.title("📚 英検2級 合格特訓 Web")
st.write("スマホでいつでも英単語・熟語の練習ができます。")

# サイドバーで設定
mode = st.sidebar.radio("学習項目を選択", ["英単語", "英熟語"])
num_q = st.sidebar.slider("出題数", 5, 50, 10)

# クイズ開始ボタン
if not st.session_state.quiz_active:
    if st.button(f"{mode}クイズを開始する", use_container_width=True):
        filename = "wordlist.txt" if mode == "英単語" else "idiomlist.txt"
        all_data = load_data(filename)
        
        if all_data:
            # ランダムに出題
            st.session_state.quiz_data = random.sample(all_data, min(len(all_data), num_q))
            st.session_state.current_idx = 0
            st.session_state.score = 0
            st.session_state.quiz_active = True
            st.session_state.is_answered = False
            st.session_state.options = []
            st.rerun()
        else:
            st.error(f"データファイル ({filename}) が見つかりません。GitHubにアップロードされているか確認してください。")

# クイズ本編
if st.session_state.quiz_active:
    q_list = st.session_state.quiz_data
    idx = st.session_state.current_idx
    
    if idx < len(q_list):
        word, correct_meaning = q_list[idx]
        
        # 選択肢の作成（その問題の最初だけ実行）
        if not st.session_state.options:
            # 他の問題の答えをダミー選択肢にする
            other_meanings = [m for w, m in q_list if m != correct_meaning]
            if len(other_meanings) < 3: # データが少ない場合の対策
                other_meanings = ["選択肢A", "選択肢B", "選択肢C"]
            
            options = random.sample(other_meanings, 3) + [correct_meaning]
            random.shuffle(options)
            st.session_state.options = options

        st.subheader(f"第 {idx + 1} 問 / {len(q_list)}")
        st.info(f"### 次の言葉の意味は？\n# {word}")

        # 4択ボタンを並べる
        for opt in st.session_state.options:
            if st.button(opt, use_container_width=True, disabled=st.session_state.is_answered):
                st.session_state.is_answered = True
                if opt == correct_meaning:
                    st.session_state.score += 1
                    st.session_state.feedback = "⭕ 正解！"
                else:
                    st.session_state.feedback = f"❌ 残念！ 正解は: {correct_meaning}"
                st.rerun()

        # 回答後のフィードバックと「次へ」ボタン
        if st.session_state.is_answered:
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
        # 全問終了時の画面
        st.balloons()
        st.header("🎉 クイズ終了！ お疲れ様でした")
        st.metric("あなたのスコア", f"{st.session_state.score} / {len(q_list)}")
        
        if st.button("トップに戻る", use_container_width=True):
            st.session_state.quiz_active = False
            st.rerun()
