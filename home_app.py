###################### IMPORTS ################################
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import streamlit as st
###################### IMPORTS ################################

###################### HELPER FUNCTIONS ################################


def elasticidade_de_preco(x_mean_price, y_demanda, nome):
    # MODELO
    # df_laptop = df_best.loc[df_best['category_name'] == 'laptop, computer',:]
    x_laptop = x_mean_price[nome]
    y_laptop = y_demanda[nome]

    results_values = {'name': [],
                      'price_elasticity': [],
                      'price_mean': [],
                      'quantity_mean': [],
                      'intercept': [],
                      'slope': [],
                      'rsquared': [],
                      'p_value': []
                      }

    X_laptop = sm.add_constant(x_laptop)

    # instanciando o modelo
    model = sm.OLS(y_laptop, X_laptop)

    # treino
    results = model.fit()

    rsquared = results.rsquared
    p_value = results.f_pvalue
    intercept, slope = results.params
    mean_price = np.mean(x_laptop)
    mean_quantity = np.mean(y_laptop)
    price_elastiscity = slope*(mean_price/mean_quantity)

    results_values['name'].append(nome)
    results_values['price_elasticity'].append(price_elastiscity)
    results_values['price_mean'].append(mean_price)
    results_values['quantity_mean'].append(mean_quantity)
    results_values['intercept'].append(intercept)
    results_values['slope'].append(slope)
    results_values['rsquared'].append(rsquared)
    results_values['p_value'].append(p_value)

    # Criar um DataFrame apenas com os valores de preço e demanda
    df_price_demand = pd.DataFrame({
        'Preço Médio': x_laptop,
        'Demanda Média': y_laptop
    })

    # Criar um novo subplot para o gráfico
    fig, ax = plt.subplots(figsize=(4, 2))

    # Plotar os pontos de dados
    ax.scatter(df_price_demand['Preço Médio'],
               df_price_demand['Demanda Média'], label='Preço e Demanda')

    # Plotar a reta de regressão
    ax.plot(df_price_demand['Preço Médio'], results.params[0] + results.params[1]
            * df_price_demand['Preço Médio'], color='red', label='Reta de Regressão')

    ax.set_xlabel('Preço ($)', fontsize=8)
    ax.set_ylabel('Demanda', fontsize=8)
    ax.set_title(
        f'Gráfico de Preço x Demanda', fontsize=10)
    ax.legend(fontsize=6)
    ax.grid(True)
    # Definir tamanho dos números nos labels dos eixos x e y
    # Definir tamanho dos números no eixo x como 8
    ax.tick_params(axis='x', labelsize=7)
    # Definir tamanho dos números no eixo y como 8
    ax.tick_params(axis='y', labelsize=7)

    # Exibir o gráfico no Streamlit
    st.pyplot(fig, use_container_width=False)

    return pd.DataFrame.from_dict(results_values)


def faturamento_elasticidade_cruzada(desconto, nome, df_cross, df_elasticidade, x_mean_price, y_demanda, lista_produtos):
    df_resultado_faturamento_total = pd.DataFrame()

    # desconto = -0.05
    for i in range(len(lista_produtos)):

        resultado_faturamento = {
            'name': [],
            'demanda_atual_outro': [],
            'demanda_nova': [],
            'faturamento_atual': [],
            'faturamento_novo': [],
            'varicao_faturamento': [],
            'variacao_percentual': []
        }

        elasticidade_cruzada = df_cross[nome + ' CPE'][i]
        # valores médios do produto com desconto
        preco_atual_medio_produto = df_elasticidade['price_mean']

        preco_atual_medio_outro = x_mean_price[lista_produtos[i]].mean()
        demanda_atual_outro = y_demanda[lista_produtos[i]].sum()

        preco_com_reducao = preco_atual_medio_produto*(1+desconto)
        # aqui usar realmente o valor de desconto dado
        aumento_demanda = desconto*elasticidade_cruzada
        demanda_nova = demanda_atual_outro*(1+aumento_demanda)

        if demanda_nova <= 0:
            demanda_nova = 0

        faturamento_atual = round(
            preco_atual_medio_outro*demanda_atual_outro, 2)
        if lista_produtos[i] == nome:
            faturamento_novo = round(preco_com_reducao[0]*demanda_nova, 2)
        else:
            faturamento_novo = round(preco_atual_medio_outro*demanda_nova, 2)
        # pensando apenas na redução de preço
        # faturamento_com_reducao = round(faturamento_atual*(1-desconto),2)
        # perda_faturamento = faturamento_atual - faturamento_com_reducao
        diferenca_faturamento = faturamento_novo - faturamento_atual
        variacao_faturamento_p = round(
            diferenca_faturamento/faturamento_atual, 2)

        resultado_faturamento['name'].append(lista_produtos[i])
        resultado_faturamento['demanda_atual_outro'].append(
            demanda_atual_outro)
        resultado_faturamento['demanda_nova'].append(demanda_nova)
        resultado_faturamento['faturamento_atual'].append(faturamento_atual)
        resultado_faturamento['faturamento_novo'].append(faturamento_novo)
        resultado_faturamento['varicao_faturamento'].append(
            diferenca_faturamento)
        resultado_faturamento['variacao_percentual'].append(
            variacao_faturamento_p)

        df_resultado_faturamento = pd.DataFrame.from_dict(
            resultado_faturamento)
        df_resultado_faturamento_total = pd.concat(
            [df_resultado_faturamento_total, df_resultado_faturamento])
    return df_resultado_faturamento_total


def substitutos_correspondentes(desconto, df_final, nome):
    df_final['demanda_aumento'] = df_final['demanda_nova'] - \
        df_final['demanda_atual_outro']
    if desconto > 0:
        return df_final.loc[(df_final['demanda_aumento'] > 0) & (df_final['name'] != nome), 'name'].tolist(), df_final.loc[(df_final['demanda_aumento'] < 0) & (df_final['name'] != nome), 'name'].tolist()
    else:
        return df_final.loc[(df_final['demanda_aumento'] < 0) & (df_final['name'] != nome), 'name'].tolist(), df_final.loc[(df_final['demanda_aumento'] > 0) & (df_final['name'] != nome), 'name'].tolist()
###################### HELPER FUNCTIONS ################################


###################### LENDOS OS ARQUIVOS ################################
df_raw = pd.read_csv('datasets/df_ready.csv')
df_cross = pd.read_csv('datasets/df_crossprice_2.csv')
###################### LENDOS OS ARQUIVOS ################################

###################### PREPARANDO O DATASET PARA A REGRESSÃO LINEAR ################################
df_raw = df_raw.drop(columns=['Unnamed: 0', 'Date_imp', 'Cluster', 'condition', 'currency',
                     'imageURLs', 'shipping', 'sourceURLs', 'weight', 'Date_imp_d.1', 'Zscore_1', 'price_std'])
df_raw.columns = ['date_imp', 'category_name', 'name', 'price', 'disc_price',
                  'merchant', 'disc_percentage', 'is_sale', 'imp_count', 'brand',
                  'p_description', 'date_added', 'date_seen', 'date_updated', 'manufacturer',
                  'day_n', 'month', 'month_n', 'day', 'week_number']
df1 = df_raw.copy()
df1['date_imp'] = pd.to_datetime(df1['date_imp'])
df_best = df1.loc[df1['merchant'] == 'Bestbuy.com', :]
df_laptop = df_best.loc[df_best['category_name'] == 'laptop, computer', :]
lista_produtos = sorted(df_laptop.name.unique().tolist())
test = df_laptop.groupby(['name', 'week_number']).agg(
    {'disc_price': 'mean', 'date_imp': 'count'}).reset_index()
x_mean_price = test.pivot(
    index='week_number', columns='name', values='disc_price')
y_demanda = test.pivot(index='week_number', columns='name', values='date_imp')
# O preço existia, mas não vendi
mediana_x = np.round(x_mean_price.median(), 2)
x_mean_price.fillna(mediana_x, inplace=True)
y_demanda.fillna(0, inplace=True)
###################### PREPARANDO O DATASET PARA A REGRESSÃO LINEAR ################################

st.set_page_config(page_title='Elasticity App',
                   layout="wide", page_icon=':dollar:')
st.header('Elasticidade de Preços dos Produtos')

produto = st.selectbox(
    'Escolha um produto para determinar a sua elasticidade de preço:',
    (lista_produtos))

###################### ELASTICIDADE INDIVIDUAL ################################
df_elasticidade = elasticidade_de_preco(x_mean_price, y_demanda, produto)
# st.dataframe(df_elasticidade.iloc[0, 1], use_container_width=True)
st.write(
    f'#### Sobre o produto: *{df_elasticidade.iloc[0, 0]}*')
if abs(df_elasticidade.iloc[0, 1]) < 1:
    st.write(
        f'#### A Elasticidade de Preço é Inelástica: {round(df_elasticidade.iloc[0, 1],2)}')
elif abs(df_elasticidade.iloc[0, 1]) == 1:
    st.write(
        f'#### A Elasticidade de Preço é Unitária: {round(df_elasticidade.iloc[0, 1],2)}')
else:
    st.write(
        f'#### A Elasticidade de Preço é Elástica: {round(df_elasticidade.iloc[0, 1],2)}')

if df_elasticidade.iloc[0, 7] > 0.05:
    st.write(
        f'#### Contudo, *não há significância estatística*, pois p valor é: {round(df_elasticidade.iloc[0, 7],4)}')
else:
    st.write(
        f'#### *Há significância estatística*, pois p valor é: {round(df_elasticidade.iloc[0, 7],4)}')

if df_elasticidade.iloc[0, 6] >= 0.5:
    st.write(
        f'#### A reta se ajusta bem aos pontos, pois o R² é: {round(df_elasticidade.iloc[0, 6],4)}')
else:
    st.write(
        f'#### A reta não se ajusta muito bem aos pontos, pois o R² é: {round(df_elasticidade.iloc[0, 6],4)}')

st.write(
    f'#### Valor médio: $ {round(df_elasticidade.iloc[0, 2],2)}')
st.write(
    f'#### Demanda média: {round(df_elasticidade.iloc[0, 3],2)} vendas por semana')
###################### ELASTICIDADE INDIVIDUAL ################################
st.divider()
###################### ELASTICIDADE CRUZADA ################################

check = st.checkbox('Utilize a elasticidade de preços cruzada')

if check:

    desconto = st.number_input(
        'Insira a variação no preço em %:', min_value=-0.15, max_value=0.15, value=0.0)

    df_final = faturamento_elasticidade_cruzada(
        desconto, produto, df_cross, df_elasticidade, x_mean_price, y_demanda, lista_produtos)

    faturamento_antigo = df_final['faturamento_atual'].sum()
    faturamento_novo = df_final['faturamento_novo'].sum()
    variacao_faturamento_total = (
        faturamento_novo-faturamento_antigo)/faturamento_antigo

    st.write(
        f'#### Faturamento anual da categoria *pré* variação: $ {round(faturamento_antigo,2)}')
    st.write(
        f'#### Faturamento anual da categoria *após* variação: $ {round(faturamento_novo,2)}')

    if variacao_faturamento_total > 0:
        st.write(
            f'#### Gerando um ganho de $ {round(faturamento_novo - faturamento_antigo,2)}')
        st.write(
            f'#### Correspondente a {round(variacao_faturamento_total*100,2)}%')
    elif variacao_faturamento_total < 0:
        st.write(
            f'#### Gerando uma perda de $ {round(faturamento_antigo - faturamento_novo,2)}')
        st.write(
            f'#### Correspondente a {round(variacao_faturamento_total*100,2)}%')
    else:
        st.write(
            f'#### Não gerando nenhuma mudança no faturamento.')
        st.write(
            f'#### Correspondente a {round(variacao_faturamento_total*100,2)}%')

    st.write(
        f'###### Observação: Esse cálculo usa apenas as elasticidades de preço que apresentam significância estatística!')
    ###################### ELASTICIDADE CRUZADA ################################
    st.divider()
    ###################### SUBSTITUTOS E CORRESPONDENTES ################################
    substitutos, correspondentes = substitutos_correspondentes(
        desconto, df_final, produto)

    if len(substitutos) > 0:
        st.write('#### Produtos Substitutos:')
        for substituto in substitutos:
            st.write(f'###### {substituto}')
    else:
        st.write('#### Não há produtos Substitutos.')

    if len(correspondentes) > 0:
        st.write('#### Produtos Correspondentes:')
        for correspondente in correspondentes:
            st.write(f'###### {correspondente}')
    else:
        st.write('#### Não há produtos Correspondentes.')

    ###################### SUBSTITUTOS E CORRESPONDENTES ################################
