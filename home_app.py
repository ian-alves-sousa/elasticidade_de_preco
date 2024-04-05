import warnings
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import statsmodels.api as sm
import streamlit as st

# Import dos dataframe
df_bp = pd.read_csv('datasets/df_resultado_faturamento.csv')
df_bp = df_bp.drop('Unnamed: 0', axis=1)
df_bp = df_bp.set_index('name')
df_c = pd.read_csv('datasets/df_crossprice.csv')
df_c = df_c.drop('Unnamed: 0', axis=1)
df_c = df_c.set_index('name')
df_elasticity = pd.read_csv('datasets/df_elastiscity.csv')
# df_elasticity = df_elasticity.drop('Unnamed: 0', axis=1)
# df_elasticity = df_elasticity.set_index('name')


################## Layout do Streamlittle #################
st.set_page_config(layout='wide')
st.header('Elasticidade de preços dos Produtos')

tab1, tab2, tab3 = st.tabs(["Elasticidade de Preços dos Produtos",
                           'Business Performance', 'Elasticidade Cruzada de Preços'])

with tab1:
    tab4, tab5 = st.tabs(
        ['Elasticidade de Preços - Gráfico', 'Elasticidade de Preços - Dataframe'])

    with tab4:
        st.header('Elasticidade de Preços - Gráfico')

        df_elasticity['ranking'] = df_elasticity.loc[:, 'price_elasticity'].rank(
            ascending=True).astype(int)
        dt_el = df_elasticity.reset_index(drop=True)

        fig, ax = plt.subplots()

        plt.figure(figsize=(12, 4))
        ax.hlines(y=dt_el['ranking'], xmin=0,
                  xmax=dt_el['price_elasticity'], color='red', alpha=1, linewidth=5)

        for name, p in zip(dt_el['name'], dt_el['ranking']):
            ax.text(4, p, name)

        for x, y, s in zip(dt_el['price_elasticity'], dt_el['ranking'], dt_el['price_elasticity']):
            ax.text(x, y, round(s, 2), horizontalalignment='right' if x < 0 else 'left',
                    verticalalignment='center',
                    fontdict={'color': 'red' if x < 0 else 'green', 'size': 10})

        # ax.gca().set(ylabel='Ranking Number', xlabel='Price Elasticity')
        # ax.title('Price Elasticity')
        ax.grid(linestyle='--')

        st.pyplot(fig)

    with tab5:
        st.header('Elasticidade de Preços - Dataframe')
        # dt_el = dt_el.set_index('ranking')
        st.dataframe(
            dt_el.loc[:, ['ranking', 'name', 'price_elasticity']], use_container_width=True)

with tab2:
    # Apresentar Business Performance
    st.header('Business Performance')
    st.dataframe(df_bp, use_container_width=True)

with tab3:
    st.header('Elasticidade Cruzada de Preços')
    st.dataframe(df_c, use_container_width=True)
