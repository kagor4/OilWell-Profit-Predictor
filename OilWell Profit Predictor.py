#!/usr/bin/env python
# coding: utf-8

# **Прогнозирование прибыли от нефтяных скважин для компании «ГлавРосГосНефть»**
# 
# ## 📋 Описание проекта
# 
# Работая в добывающей компании «ГлавРосГосНефть», я разработал модель машинного обучения для выбора оптимального региона бурения новых нефтяных скважин. Проект включает анализ данных о пробах нефти в трёх регионах, обучение модели для предсказания объёма запасов, оценку прибыли и анализ рисков с использованием техники Bootstrap. Цель — определить регион с максимальной суммарной прибылью при минимальных рисках.
# 
# 
# ## 🎯 Задачи проекта
# 
# - Провести анализ характеристик скважин в трёх регионах
# - Построить модель для предсказания объёма запасов нефти
# - Отобрать скважины с наивысшими предсказанными запасами
# - Рассчитать потенциальную прибыль для каждого региона
# - Оценить риски и неопределённость с помощью Bootstrap
# - Выбрать регион с наибольшей суммарной прибылью
# 
# ## 📊 Данные
# 
# Данные содержат информацию о скважинах в трёх регионах:
# - **Признаки**:
#   - `id` — уникальный идентификатор скважины
#   - `f0`, `f1`, `f2` — три значимых признака (характеристики скважин)
# - **Целевая переменная**:
#   - `product` — объём запасов в скважине (тыс. баррелей)

# ## Загрузка и подготовка данных

# In[1]:


import pandas as pd
import os
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from numpy.random import RandomState
from tqdm import tqdm


# In[2]:


def calculate_profit(true_values, predicted_values):
    sorted_predictions = pd.Series(predicted_values).sort_values(ascending=False)[:points_200]
    true_values_sorted = (true_values.reset_index(drop=True)[sorted_predictions.index])
    total_true_values = true_values_sorted.sum() 
    return round((total_true_values * price_per_barrel) - budget, 2)


# In[3]:


def calculate_confidence_interval(true_values, predicted_values):
    bootstrap_samples = []
    state = np.random.RandomState(12345)
    for i in tqdm(range(1000)):
        bootstrap_sample = pd.Series(predicted_values).sample(n=points_500, replace=True, random_state=state)
        bootstrap_samples.append(calculate_profit(true_values, bootstrap_sample))
    
    bootstrap_samples = pd.Series(bootstrap_samples)
    print(bootstrap_samples.mean())
    print(bootstrap_samples.apply(lambda x: x < 0).sum() / len(bootstrap_samples) * 100, "%")
    
    lower_bound = bootstrap_samples.quantile(0.025)
    upper_bound = bootstrap_samples.quantile(0.975)
    return round(lower_bound, 2), round(upper_bound, 2)


# Загружу и проверю на пропуски, дубликаты и корреляцию данные по первому региону

# In[4]:


data_geo_1 = '/datasets/geo_data_0.csv'

if os.path.exists(data_geo_1):
    df_geo_1 = pd.read_csv(data_geo_1)
else:
    print('Something is wrong')


# In[5]:


df_geo_1.head()


# In[6]:


df_geo_1.info()


# In[7]:


df_geo_1.describe()


# In[8]:


df_geo_1.duplicated().sum()


# In[9]:


df_geo_1.corr()


# Пропусков в значениях нет, дубликаты так же отсутствуют, аномалий в данных не наблюдаются. Корреляция признаков относительно дргу друга - в пределах допустимого.

# Загружу и проверю на пропуски, дубликаты и корреляцию данные по второму региону

# In[10]:


data_geo_2 = '/datasets/geo_data_1.csv'

if os.path.exists(data_geo_2):
    df_geo_2 = pd.read_csv(data_geo_2)
else:
    print('Something is wrong')


# In[11]:


df_geo_2.head()


# In[12]:


df_geo_2.info()


# In[13]:


df_geo_2.describe()


# In[14]:


df_geo_2.duplicated().sum()


# In[15]:


df_geo_2.corr()


# Пропусков в значениях нет, дубликаты так же отсутствуют, аномалий в данных не наблюдаются. Признак f2 сильно коррелируют с целевым, по этому от него следует избавиться.

# In[16]:


# df_geo_2_without_f2 = df_geo_2.drop(["f2"],axis = 1)


# Загружу и проверю на пропуски, дубликаты и корреляцию данные по третьему региону

# In[17]:


data_geo_3 = '/datasets/geo_data_2.csv'

if os.path.exists(data_geo_3):
    df_geo_3 = pd.read_csv(data_geo_3)
else:
    print('Something is wrong')


# In[18]:


df_geo_3.head()


# In[19]:


df_geo_3.info()


# In[20]:


df_geo_3.describe()


# In[21]:


df_geo_3.duplicated().sum()


# In[22]:


df_geo_3.corr()


# Пропусков в значениях нет, дубликаты так же отсутствуют, аномалий в данных не наблюдаются. Корреляция признаков относительно дргу друга - в пределах допустимого.

# ## Обучение и проверка модели

# Обучим и проверим модель на выборке по первому региону

# In[23]:


features = df_geo_1.drop(["id","product"], axis = 1)
target = df_geo_1["product"]

features_train, features_valid_first, target_train, target_valid_first = train_test_split(
    features, target, test_size=0.25, random_state=12345)

model = LinearRegression()
model.fit(features_train, target_train)
predictions_valid_first = model.predict(features_valid_first)
result = mean_squared_error(target_valid_first, predictions_valid_first) ** 0.5
print("RMSE модели линейной регрессии первого региона на валидационной выборке:", result)


# In[24]:


df_geo_1_mean_values = df_geo_1["product"].mean()
print(f"Средний запас первого региона составляет: {df_geo_1_mean_values:.4f} тысяч баррелей")


# Обучим и проверим модель на выборке по второму региону

# In[25]:


features = df_geo_2.drop(["id","product"], axis = 1)
target = df_geo_2["product"]

features_train, features_valid_second, target_train, target_valid_second = train_test_split(
    features, target, test_size=0.25, random_state=12345)

model = LinearRegression()
model.fit(features_train, target_train)
predictions_valid_second = model.predict(features_valid_second)
result = mean_squared_error(target_valid_second, predictions_valid_second) ** 0.5
print("RMSE модели линейной регрессии второго региона на валидационной выборке:", result)


# In[26]:


df_geo_2_mean_values = df_geo_2["product"].mean()
print(f"Средний запас второго региона составляет: {df_geo_2_mean_values:.4f} тысяч баррелей")


# Обучим и проверим модель на выборке по третьему региону

# In[27]:


features = df_geo_3.drop(["id","product"], axis = 1)
target = df_geo_3["product"]

features_train, features_valid_third, target_train, target_valid_third = train_test_split(
    features, target, test_size=0.25, random_state=12345)

model = LinearRegression()
model.fit(features_train, target_train)
predictions_valid_third = model.predict(features_valid_third)
result = mean_squared_error(target_valid_third, predictions_valid_third) ** 0.5
print("RMSE модели линейной регрессии третьего региона на валидационной выборке:", result)


# In[28]:


df_geo_3_mean_values = df_geo_3["product"].mean()
print(f"Средний запас третьего региона составляет: {df_geo_3_mean_values:.4f} тысяч баррелей")


# Вывод:
# 1. В первом регионе ошибка самая маленькая, но по среднему количеству запаса сырья он стоит на втором месте
# 2. Во втором регионе наблюдается самая большая ошибка, а так же по среднему запасу сырья стоит на последнем месте
# 3. В третьем регионе ошибка идет на втором месте, но по показателю среднего объема сырья регион стоит на первом месте

# ## Подготовка к расчёту прибыли

# In[29]:


budget = 10000000000
points_500 = 500
points_200 = 200
price_per_barrel = 450000
loss_probability = 0.025
non_loss_points = (budget/(price_per_barrel*1000))/points_200

print("Достаточный объём сырья для безубыточной разработки новой скважины: {:.2f} тысяч баррелей".format(non_loss_points))


# In[30]:


percentage_above_threshold_geo_1 = (df_geo_1['product'] >= non_loss_points*1000).mean() * 100
print(f"Процент безубыточных скважин в первом регионе: {percentage_above_threshold_geo_1:.2f}%")


# In[31]:


percentage_above_threshold_geo_2 = (df_geo_2['product'] >= non_loss_points*1000).mean() * 100
print(f"Процент безубыточных скважин во втором регионе: {percentage_above_threshold_geo_2:.2f}%")


# In[32]:


percentage_above_threshold_geo_3 = (df_geo_3['product'] >= non_loss_points*1000).mean() * 100
print(f"Процент безубыточных скважин в третьем регионе: {percentage_above_threshold_geo_3:.2f}%")


# Исходя из представленных данных, можно сделать следующие общие выводы:
# 
# Для безубыточной разработки новой скважины необходимо, чтобы объем сырья составлял не менее 0.11 тысяч баррелей.
# 
# - Первый регион обладает наивысшим процентом безубыточных скважин среди трех регионов, составляя 36.58%. При этом средний запас скважины в этом регионе достаточно высок и составляет 92.5000 тысяч баррелей.
# 
# - Второй регион имеет самый низкий процент безубыточных скважин (16.54%) среди всех регионов, и средний запас скважины в этом регионе также меньше по сравнению с первым регионом, составляя 68.8250 тысяч баррелей.
# 
# - Третий регион демонстрирует высокий процент безубыточных скважин (38.18%) и имеет средний запас на уровне 95.0000 тысяч баррелей.
# 
# Таким образом, на основе анализа данных, третий регион представляется наиболее перспективным для разработки новых скважин, учитывая как процент безубыточных скважин, так и средний запас сырья.

# ## Расчёт прибыли и рисков 

# In[33]:


top_200_first_region = calculate_profit(target_valid_first, predictions_valid_first)
print("Прибыль с лучших 200 скважин в первом регионе:", top_200_first_region)


# In[34]:


top_200_second_region = calculate_profit(target_valid_second, predictions_valid_second)
print("Прибыль с лучших 200 скважин во втором регионе:", top_200_second_region)


# In[35]:


top_200_third_region = calculate_profit(target_valid_third, predictions_valid_third)
print("Прибыль с лучших 200 скважин в третьем регионе:", top_200_third_region)


# In[36]:


print("95% доверительный итервал для первого региона лежит между:",
      calculate_confidence_interval(target_valid_first, pd.Series(predictions_valid_first)))


# In[37]:


print("95% доверительный итервал для второго региона лежит между:",
      calculate_confidence_interval(target_valid_second, pd.Series(predictions_valid_second)))


# In[38]:


print("95% доверительный итервал для первого региона лежит между:",
      calculate_confidence_interval(target_valid_third, pd.Series(predictions_valid_third)))


# Исходя из представленных данных, можно сделать следующие общие выводы:
# 
# Первый регион:
# 
# - Прибыль с лучших 200 скважин составляет 3,320,826,043.14.
# - Средняя прибыль с одной скважины: 396,164,984.80.
# - Риски: 6.9%.
# - 95% доверительный интервал: (-111,215,545.89, 909,766,941.55).
# 
# Второй регион:
# 
# - Прибыль с лучших 200 скважин составляет 2,415,086,696.68.
# - Средняя прибыль с одной скважины: 456,045,105.78.
# - Риски: 1.5%.
# - 95% доверительный интервал: (-4,286,021,657.67, -3,131,804,233.85).
# 
# Третий регион:
# 
# - Прибыль с лучших 200 скважин составляет 2,710,349,963.60.
# - Средняя прибыль с одной скважины: 404,403,866.57.
# - Риски: 7.6%.
# - 95% доверительный интервал: (-163,350,413.39, 950,359,574.93).
# 
# Общие выводы:
# 
# Второй регион выделяется как наиболее стабильный и прибыльный среди трех, что делает его наилучшим выбором для разработки, учитывая ограничения по рискам и бюджету. Риски в данном регионе минимальны – всего 1.5%, что удовлетворяет условиям задания, где требуется оставить регион с вероятностью убытков менее 2.5%.
# Первый и третий регионы также предоставляют перспективы для разработки, но следует тщательно взвесить риски и потенциальную прибыль перед окончательным решением.
