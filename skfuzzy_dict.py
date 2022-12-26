import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl
from operator import itemgetter

class DictFuzzy:
    def __init__(self):
        pass
    #參數:(營養成分名稱, 指標上限值, 合適程度(y)隶属度函数)
    def __upper(self, nutrient_name, x_upper, y_sub): #限制(上限)
        x_middle = x_upper * 0.5
        x_stop = x_upper * 1.5
        x_range= np.arange(0, x_stop, 1, np.float64)
        x = ctrl.Antecedent(x_range, nutrient_name) # 創建模糊控制變數
        ##定義模糊集和其隸屬度函數
        x['S'] = fuzz.trimf(x_range, [0, x_middle, x_upper])
        x['TH'] = fuzz.trimf(x_range, [x_upper, x_stop, x_stop])
        ## 输出規則
        r1 = ctrl.Rule(x['TH'] , y_sub['L'])
        r3 = ctrl.Rule(x['S'] , y_sub['H'])
        x.view()
        return  [r1, r3]

    def __interval(self, nutrient_name, x_lower, x_upper, y_sub): #區間
        x_middle = (x_lower + x_upper) * 0.25
        x_stop = (x_lower + x_upper) * 0.75
        x_range= np.arange(0, x_stop, 1, np.float64)
        x =ctrl.Antecedent(x_range, nutrient_name)
        x['TL'] = fuzz.trimf(x_range, [0, 0, x_lower]) #過低
        x['S'] = fuzz.trimf(x_range, [0, x_middle, (x_lower + x_upper)]) #合適 
        x['TH'] = fuzz.trimf(x_range, [x_upper, x_stop, x_stop]) #過高
        r1 = ctrl.Rule(x['TL'] | x['TH'] , y_sub['L'])
        r2 = ctrl.Rule(x['S'] , y_sub['H'])
        return [r1, r2]

    def __suitability(self): #合適程度
        y_range = np.arange(0, 100, 1, np.float64)
        y = ctrl.Consequent(y_range, 'suitability')
        y['L'] = fuzz.trimf(y_range, [0, 0, 50]) #低
        y['M'] = fuzz.trimf(y_range, [0, 50, 100]) #中
        y['H'] = fuzz.trimf(y_range, [50, 100, 100]) #高
        return  {'L': y['L'], 'M': y['M'], 'H': y['H']}
    
    #參數:使用者疾病, 使用者一日飲食指標, 加入此關鍵詞食物後營養素
    def get_lst_dict(self, lst_user_diseases, dic_indicators_day, lst_dic_all_user_nutrients, lst_recommend_score):
        lst_rules = []
        lst_antecedents = []
        so_count = 0
        fs_count = 0
        sf_count = 0
        fa_count = 0
        y_sub = self.__suitability()
        for disease in lst_user_diseases:
            if disease == 'ckd':
                lst_rules += self.__interval('protein', dic_indicators_day['protein_lower'], dic_indicators_day['protein_upper'], y_sub)
                lst_antecedents += ['protein']
            if ((disease == 'htn') | (disease == 'ckd')) & (so_count == 0):
                lst_rules += self.__upper('sodium', dic_indicators_day['sodium_upper'], y_sub)
                lst_antecedents += ['sodium']
                so_count += 1
            if ((disease == 'cvd') | (disease == 'dm')) & (fs_count == 0):
                lst_rules += self.__upper('free_sugar', dic_indicators_day['free_sugar_upper'], y_sub)
                lst_antecedents += ['free_sugar']
                fs_count += 1
            if disease == 'cvd':
                lst_rules += self.__interval('fat', dic_indicators_day['fat_lower'], dic_indicators_day['fat_upper'], y_sub)
                lst_antecedents += ['fat']
            if ((disease == 'cvd') | (disease == 'dm')) & (sf_count == 0):
                lst_rules += self.__interval('saturated_fat', dic_indicators_day['saturated_fat_lower'], dic_indicators_day['saturated_fat_upper'], y_sub)
                lst_antecedents += ['saturated_fat']
                sf_count += 1
            if disease == 'dm':
                lst_rules += self.__upper('carbohydrate', dic_indicators_day['carbohydrate_upper'], y_sub)
                lst_antecedents += ['carbohydrate']
            if ((disease == 'dm') | (disease == 'htn')) & (fa_count == 0):
                lst_rules += self.__upper('fat', dic_indicators_day['fat_upper'], y_sub)
                lst_antecedents += ['fat']
                fa_count += 1
            if disease == 'htn':
                lst_rules += self.__upper('saturated_fat', dic_indicators_day['saturated_fat_upper'], y_sub)
                lst_antecedents += ['saturated_fat']

        suitability_ctrl = ctrl.ControlSystem(rules=lst_rules)
        suitability = ctrl.ControlSystemSimulation(suitability_ctrl)
        
        for i in range(0,len(lst_dic_all_user_nutrients)):
            for a in lst_antecedents:
                suitability.input[a] = lst_dic_all_user_nutrients[i][a] #設定前提(antecedents)值
                # print(i, a, lst_dic_all_user_nutrients[i][a])
            suitability.compute() #計算
            lst_dic_all_user_nutrients[i].setdefault('output', suitability.output['suitability']*lst_recommend_score[i]) #將結果值存入該食物dict
            # print(i, "###output", suitability.output['suitability'])
        lst_dict = sorted(lst_dic_all_user_nutrients, key=itemgetter("output"), reverse = True) #根據Fuzzy輸出值排序
        return lst_dict