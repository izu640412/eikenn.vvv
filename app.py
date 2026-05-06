import tkinter as tk
from tkinter import messagebox, ttk
import random
import os
import json

class WordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("英検2級 合格特訓アプリ")
        self.root.geometry("500x750")
        self.root.configure(bg="#f8f9fa")

        # 設定値
        self.time_limit = 10.0
        self.max_questions = 20

        # データ読み込み
        self.all_words_list = self.load_data("wordlist.txt")
        self.all_idioms_list = self.load_data("idiomlist.txt")
        
        self.score_file = os.path.join(os.path.dirname(__file__), "scores.json")
        self.high_scores = self.load_scores()
        self.timer_job = None

        # 画像読み込み
        self.dog_img = None
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dog_path = os.path.join(base_dir, "dog.png")
        if os.path.exists(dog_path):
            try: self.dog_img = tk.PhotoImage(file=dog_path)
            except: pass

        self.main_frame = tk.Frame(self.root, bg="#f8f9fa")
        self.main_frame.pack(fill="both", expand=True)

        self.show_top_menu()

    def load_data(self, filename):
        data_list = []
        file_path = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    data = line.strip().split(",")
                    if len(data) >= 2:
                        data_list.append((data[0].strip(), data[1].strip()))
        return data_list

    def load_scores(self):
        if os.path.exists(self.score_file):
            try:
                with open(self.score_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: return {}
        return {}

    def save_score(self, range_key, score):
        current_high = self.high_scores.get(range_key, 0)
        if score > current_high:
            self.high_scores[range_key] = score
            with open(self.score_file, "w", encoding="utf-8") as f:
                json.dump(self.high_scores, f)

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_top_menu(self):
        """トップメニュー画面"""
        self.clear_frame()
        tk.Button(self.main_frame, text="⚙ 設定", font=("Arial", 10), bg="#ecf0f1",
                  command=self.show_settings).place(x=430, y=10)

        tk.Label(self.main_frame, text="英検2級 合格特訓", 
                 font=("MS Gothic", 26, "bold"), bg="#f8f9fa", fg="#2c3e50").pack(pady=50)

        if self.dog_img:
            tk.Label(self.main_frame, image=self.dog_img, bg="#f8f9fa").pack(pady=10)

        tk.Label(self.main_frame, text="学習項目を選択してください", 
                 font=("MS Gothic", 12), bg="#f8f9fa", fg="#7f8c8d").pack(pady=20)

        tk.Button(self.main_frame, text="📚 英単語 (Words)", font=("MS Gothic", 16, "bold"),
                  width=25, height=3, bg="#3498db", fg="white", relief="flat",
                  command=lambda: self.show_selection_menu("word")).pack(pady=15)

        tk.Button(self.main_frame, text="💡 英熟語 (Idioms)", font=("MS Gothic", 16, "bold"),
                  width=25, height=3, bg="#e67e22", fg="white", relief="flat",
                  command=lambda: self.show_selection_menu("idiom")).pack(pady=15)

    def show_selection_menu(self, mode):
        """番号選択画面（1列表示・スクロール対応）"""
        self.clear_frame()
        
        title = "📚 英単語 選択" if mode == "word" else "💡 英熟語 選択"
        data_list = self.all_words_list if mode == "word" else self.all_idioms_list
        prefix = "word" if mode == "word" else "idiom"
        btn_color = "#3498db" if mode == "word" else "#e67e22"

        tk.Button(self.main_frame, text="◀ 戻る", font=("Arial", 10), bg="#ecf0f1",
                  command=self.show_top_menu).place(x=10, y=10)

        tk.Label(self.main_frame, text=title, font=("MS Gothic", 20, "bold"), bg="#f8f9fa").pack(pady=30)

        canvas = tk.Canvas(self.main_frame, bg="#f8f9fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f8f9fa")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=460) # 横幅を固定して中央寄せ
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")

        # マウスホイール対応
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ボタンを1列に生成
        chunk_size = 100
        for i in range(0, len(data_list), chunk_size):
            start = i
            end = min(i + chunk_size, len(data_list))
            range_key = f"{prefix}_{start+1}-{end}"
            
            btn_frame = tk.Frame(scrollable_frame, bg="#f8f9fa")
            btn_frame.pack(pady=12, fill="x")

            btn = tk.Button(btn_frame, text=f"No. {start+1} - {end}", 
                            font=("MS Gothic", 12, "bold"),
                            width=30, height=2, bg=btn_color, fg="white", relief="flat",
                            command=lambda d=data_list, s=start, e=end, k=range_key: self.start_quiz(d, s, e, k))
            btn.pack()
            
            high_score = self.high_scores.get(range_key, 0)
            tk.Label(btn_frame, text=f"Best Score: {high_score} / {self.max_questions}", 
                     font=("Arial", 10), bg="#f8f9fa", fg="#27ae60").pack()

    def show_settings(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="アプリ設定", font=("MS Gothic", 20, "bold"), bg="#f8f9fa").pack(pady=30)
        q_label = tk.Label(self.main_frame, text=f"出題数: {self.max_questions}問", font=("Arial", 12), bg="#f8f9fa")
        q_label.pack(pady=5)
        def update_q_label(val): q_label.config(text=f"出題数: {int(float(val))}問")
        q_slider = ttk.Scale(self.main_frame, from_=5, to=20, orient="horizontal", length=300, command=update_q_label)
        q_slider.set(self.max_questions)
        q_slider.pack(pady=10)
        t_label = tk.Label(self.main_frame, text=f"制限時間: {int(self.time_limit)}秒", font=("Arial", 12), bg="#f8f9fa")
        t_label.pack(pady=20)
        def update_t_label(val): t_label.config(text=f"制限時間: {int(float(val))}秒")
        t_slider = ttk.Scale(self.main_frame, from_=3, to=20, orient="horizontal", length=300, command=update_t_label)
        t_slider.set(self.time_limit)
        t_slider.pack(pady=10)
        def save_and_back():
            self.max_questions = int(q_slider.get()); self.time_limit = float(int(t_slider.get()))
            self.show_top_menu()
        tk.Button(self.main_frame, text="保存して戻る", font=("MS Gothic", 14), bg="#2ecc71", fg="white", width=20, height=2, command=save_and_back).pack(pady=50)

    def start_quiz(self, data_list, start, end, range_key):
        self.current_range_key = range_key
        selected_data = data_list[start:end]
        num_to_select = min(len(selected_data), self.max_questions)
        self.quiz_queue = random.sample(selected_data, num_to_select)
        self.current_dict = dict(selected_data)
        self.question_count = 0; self.correct_count = 0; self.current_max = num_to_select
        self.setup_quiz_ui(); self.next_question()

    def setup_quiz_ui(self):
        self.clear_frame()
        self.info_label = tk.Label(self.main_frame, text="", font=("Arial", 11), bg="#f8f9fa"); self.info_label.pack(pady=5)
        self.canvas = tk.Canvas(self.main_frame, width=500, height=40, bg="#ecf0f1", highlightthickness=0); self.canvas.pack(fill="x")
        self.gauge = self.canvas.create_rectangle(0, 35, 500, 40, fill="#2ecc71", outline="")
        if self.dog_img: self.dog_mark = self.canvas.create_image(500, 35, image=self.dog_img, anchor="s")
        else: self.dog_mark = self.canvas.create_oval(480, 15, 500, 35, fill="#3498db", outline="")
        self.label_q = tk.Label(self.main_frame, text="", font=("Arial", 26, "bold"), bg="#f8f9fa", wraplength=450); self.label_q.pack(pady=30)
        self.btns = []
        for i in range(4):
            btn = tk.Button(self.main_frame, text="", font=("MS Gothic", 12), width=40, height=2, bg="#ffffff", command=lambda idx=i: self.check_answer(idx))
            btn.pack(pady=5); self.btns.append(btn)

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 0.1; width = (self.time_left / self.time_limit) * 500
            color = "#2ecc71" if self.time_left > 3 else "#e74c3c"
            self.canvas.coords(self.gauge, 0, 35, width, 40); self.canvas.itemconfig(self.gauge, fill=color)
            if self.dog_img: self.canvas.coords(self.dog_mark, width, 35)
            self.timer_job = self.root.after(100, self.update_timer)
        else: self.next_question()

    def check_answer(self, idx):
        if self.timer_job: self.root.after_cancel(self.timer_job)
        selected = self.options[idx]; correct = self.current_dict.get(self.current_q)
        for b in self.btns: b.config(state="disabled")
        if selected == correct:
            self.correct_count += 1; self.btns[idx].config(bg="#d4edda", disabledforeground="black"); self.root.after(800, self.next_question)
        else:
            self.btns[idx].config(bg="#f8d7da", disabledforeground="black")
            for i in range(4):
                if self.options[i] == correct: self.btns[i].config(bg="#d4edda", disabledforeground="black")
            self.root.after(2000, self.next_question)

    def next_question(self):
        if self.timer_job: self.root.after_cancel(self.timer_job)
        if self.question_count >= self.current_max:
            self.save_score(self.current_range_key, self.correct_count)
            messagebox.showinfo("終了", f"結果: {self.correct_count} / {self.current_max}")
            self.show_top_menu()
            return
        q_word, q_meaning = self.quiz_queue[self.question_count]
        self.current_q = q_word; self.question_count += 1
        self.info_label.config(text=f"第 {self.question_count} 問 / {self.current_max}")
        all_meanings = list(self.current_dict.values())
        other = [m for m in all_meanings if m != q_meaning]
        self.options = random.sample(other, 3) + [q_meaning]; random.shuffle(self.options)
        self.label_q.config(text=self.current_q)
        for i in range(4): self.btns[i].config(text=self.options[i], bg="#ffffff", state="normal")
        self.time_left = self.time_limit; self.update_timer()

if __name__ == "__main__":
    root = tk.Tk(); app = WordApp(root); root.mainloop()