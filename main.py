from random import choice

word_dict = {}

# 1. ファイルを読み込む
try:
    with open("wordlist.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()  
            if not line or "," not in line:
                continue
            
            # カンマで分割
            data = line.split(",")
            
            # 【重要】ここをファイルの中身に合わせて調整してください
            # ファイルが「英語,日本語」の順ならこのまま
            # ファイルが「日本語,英語」の順なら [1] と [0] を入れ替えてください
            english = data[0].strip()
            japanese = data[1].strip()
            
            if english: # 英語（問題）が空じゃないときだけ登録
                word_dict[english] = japanese

except FileNotFoundError:
    print("エラー：wordlist.txtが見つかりません。")

# 2. クイズを出題
if word_dict:
    # 全単語の中から、空っぽじゃないものを抽出
    valid_keys = [k for k in word_dict.keys() if k]
    
    if valid_keys:
        問題 = choice(valid_keys)
        print(f"\n問題: {問題}")
        
        回答 = input("日本語の意味を入力してください: ")

        # 3. 判定
        if 回答.strip() == word_dict[問題]:
            print("★正解！")
        else:
            print(f"×残念。正解は「{word_dict[問題]}」でした。")
    else:
        print("有効な単語が見つかりませんでした。")
else:
    print("単語を読み込めませんでした。wordlist.txt の中身（カンマなど）を確認してください。")