import random

#integral特性探索
def integral():
    attempt = 10**3   # 段鍵、平文のランダム設定の回数
    floor = 2     # 何回差分か
    round = int(input("何段目のIntegral特性を求めますか? :"))

    #出力部のIntegral特性
    for i in range(attempt):
        #仮の平文(実際の平文は17~20行で作る)をランダムに設定 64bits
        plain_text = random.randint(0x0000000000000000,0xffffffffffffffff)
        #鍵をランダムに設定 128bits
        key = random.randint(0x00000000000000000000000000000000,0xffffffffffffffffffffffffffffffff)
        
        #integral特性(ランダムに生成されたplain_textをaa...accc...cというパターンに変更し、これを実際の平文とする)       
        output_list = []
        for j in range(round):
            output_list.append([0]*64)

        # 各段ごとのある平文・鍵に対する特性のリスト        
        output_integral = []
        for j in range(round):
            output_integral.append("")

        # 1つのn階差分入力に対する各段の暗号文のbti毎の1のカウント
        for delta_p in range(2**floor):
            # 暗号文を得る                                 
            cryptgram = DoT(plain_text ^ (delta_p<<(64-floor)), key, round)
            #cryptgram = DoT(plain_text ^ delta_p, key, round)
            
            # 1の数え上げ
            for j in range(round):
                for k in range(64):
                    output = (cryptgram[j]>>(64-k)) & 0x1
                    output_list[j][k] += output

        # 1つのn階差分入力に対するbit毎の1のカウントをIntegral特性に変換する
        for l in range(round):
            for m in range(64):
                if output_list[l][m]%2==0:
                    output_integral[l] += "b"
                else:
                    output_integral[l] += "u"
        
        # 全体のIntegral特性を更新する
        if i==0:
            # 初回のみコピー
            output_list_ByKey = output_integral
        else:
            # Integral特性を更新する
            for n in range(round):
                # 各段のIntegral特性を取り出す
                output_integral_element = output_integral[n]
                # 各段の蓄積されたIntegral特性を取り出す
                output_list_ByKey_element = output_list_ByKey[n]
                
                # Integral特性の蓄積結果をbit毎に更新する
                for o in range(64):
                    if output_integral_element[o]==output_list_ByKey_element[o] or output_list_ByKey_element[o]=="u":
                        pass
                    elif output_integral_element[o]=="u":
                        output_list_ByKey_element = output_list_ByKey_element[:o] + "u" + output_integral_element[o+1:]

                    else:
                        output_list_ByKey_element = output_list_ByKey_element[:o] + "b" + output_integral_element[o+1:]

                output_integral[n] = output_integral_element
                output_list_ByKey[n] = output_list_ByKey_element

    for p in range(round):
        result = output_list_ByKey[p]
        print(p+1,"段の出力結果",result)


#暗号器
def DoT(plaintext, key, round):
    
    """
    plaintext, key, roundを入れることにより、roundで指定した段の出力を
    返してくれる関数
    """
    s = [0x3, 0xf, 0xe, 0x1, 0x0, 0xa, 0x5, 0x8, 0xc, 0x4, 0xb, 0x2, 0x9, 0x7, 0x6, 0xd]
    permutation=[52,54,48,55,49,51,53,2,4,6,0,7,1,3,5,18,20,22,16,23,17,19,21,34,36,38,32,39,33,35,37,50,12,14,8,15,9,11,13,26,28,30,24,31,25,27,29,42,44,46,40,47,41,43,45,58,60,62,56,63,57,59,61,10]
    K = key
    roundkey = []
    for i in range(1, round+1):              # 段鍵生成
        roundkey.append(K >> 64)
        UK = ((K<<13) & 0xffffffffffffffffffffffffffffffff) ^ (K>>115)
        T_1 = (UK>>124) & 0xf
        T_2 = (UK>>120) & 0xf
        T_1_Sb = s[T_1]
        T_2_Sb = s[T_2]
        K = (T_1_Sb<<124) | (T_2_Sb<<120) | ((UK<<8)>>8) ^ (i<<59)

    round_output_list =[]
    round_input = plaintext
    for i in range(round):                   # 段鍵と入力をXOR
        before_Sbox = round_input ^ roundkey[i]

        division_64_4 = []
        for j in range(16):                  # 64bitを4bitごとに分け、S-boxへ通す
            division_4 = (before_Sbox >> (j*4)) & 0xf
            division_4 = s[division_4]
            division_64_4.insert(0, division_4)

        division_64_1 = []
        for k in range(0,16):              # 64bitを1bitごとに分ける
            for temp in range(4):
                division_64_1.append(division_64_4[k]>>(3-temp) & 1)
        
        p = []
        for pm in range(64):
            p.append(0)
        
        for perm in range(64):
            p[permutation[perm]] = division_64_1[perm]
        
        final = 0x0000000000000000
        for bit in range(64):
            final = final ^ (p[bit]<<(63-bit))

        round_output = final
        round_output_list.append(round_output)
        round_input = round_output
    
    return round_output_list
    #return round_output

if __name__ == "__main__":
    integral()