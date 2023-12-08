import streamlit as st
import os
import pandas as pd
import  base64
import plotly.express as px
from io import BytesIO

# Função para filtrar a multiseleção de categorias
def multiselect_filter(df, column, selected_values):
    if selected_values:
        return df[df[column].isin(selected_values)]
    return df

# Função para download em excel
def download_excel(dataframe, filename, sheet_name='Sheet1'):
    output = BytesIO()
    excel_writer = pd.ExcelWriter(output, engine='xlsxwriter')
    dataframe.to_excel(excel_writer, sheet_name=sheet_name, index=True)
    excel_writer.close()
    excel_data_excel = output.getvalue()
    b64 = base64.b64encode(excel_data_excel).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx">Download Excel</a>'
    return href

# Configuração da página
st.set_page_config(page_title = 'Análise de Telemarketing',
                    page_icon = 'C:/Users/adilt/Desktop/Ebac/Notebooks/Cientista de dados/Mod19/img/telmarketing_icon.png',
                    layout = "wide",
                    initial_sidebar_state = 'expanded')

# Título da aplicação
st.title('Análise de Telemarketing')
st.markdown("---")

# Caminho para a pasta onde está localizada a imagem
path_to_image = 'C:/Users/adilt/Desktop/Ebac/Notebooks/Cientista de dados/Mod19/img/Bank-Branding.jpg'

# Verifica se o arquivo de imagem existe no caminho especificado
if os.path.exists(path_to_image):
    uploaded_image = open(path_to_image, 'rb').read()
    st.sidebar.image(uploaded_image, use_column_width=True)
else:
    st.sidebar.warning('Imagem não encontrada')

# Upload da base de dados
uploaded_file = st.sidebar.file_uploader("Upload da Base de Dados CSV", type='csv')

# Mostra a tabela com os dados originais, se a base for carregada
if uploaded_file is not None:
    base_real = pd.read_csv(uploaded_file, sep=';')
    base_copia = base_real.copy()
    st.subheader('Dados Originais')
    # Contagem de linhas do dataframe base real sem o cabeçalho
    st.write(f"Total de linhas: {base_real.shape[0]}")
    st.write(base_real)

    # Título do menu
    st.sidebar.title('Menu')

    # Definir opção para seleção de gráfico
    tipo_grafico = st.sidebar.radio("Selecione o Tipo de Gráfico", ('Barras', 'Pizza'))

    # Filtro de idade
    idade_min = int(base_copia['age'].min())
    idade_max = int(base_copia['age'].max())
    idade_selecao = st.sidebar.slider("Idade:", idade_min, idade_max, (idade_min, idade_max))
    
    # Filtro de empregos
    emprego_lista = base_copia['job'].unique().tolist()
    emprego_selecao = st.sidebar.multiselect('Profissão', emprego_lista)
        
    # Filtro de estado civil
    estado_civil_lista = base_copia['marital'].unique().tolist()
    estado_civil_selecao = st.sidebar.multiselect('Estado civil', estado_civil_lista)

    # Filtro de default
    default_lista = base_copia['default'].unique().tolist()
    default_selecao = st.sidebar.multiselect('Default', default_lista)

    # Filtro de financiamento imobiliário
    financiamento_lista = base_copia['housing'].unique().tolist()
    financiamento_selecao = st.sidebar.multiselect('Financiamento Imobiliário?', financiamento_lista)

    # Filtro de empréstimo
    emprestimo_lista = base_copia['loan'].unique().tolist()
    emprestimo_selecao = st.sidebar.multiselect('Empréstimo?', emprestimo_lista)

    # Filtro de meio de contato
    contato_lista = base_copia['contact'].unique().tolist()
    contato_selecao = st.sidebar.multiselect('Meio de Contato', contato_lista)

    # Filtro de mês
    mes_lista = base_copia['month'].unique().tolist()
    mes_selecao = st.sidebar.multiselect('Mês(es)', mes_lista)

    # Filtro de dia da semana
    dia_da_semana_lista = base_copia['day_of_week'].unique().tolist()
    dia_da_semana_selecao = st.sidebar.multiselect('Dia(s) da semana', dia_da_semana_lista)

    aplicar_filtro = st.sidebar.button('Aplicar')

    # Encadeamento de métodos para aplicar os filtros
    if aplicar_filtro:
        base_filtrada = (base_copia.query("age >= @idade_selecao[0] and age <= @idade_selecao[1]")
            .pipe(multiselect_filter, 'job', emprego_selecao)
            .pipe(multiselect_filter, 'marital', estado_civil_selecao)
            .pipe(multiselect_filter, 'default', default_selecao)
            .pipe(multiselect_filter, 'housing', financiamento_selecao)
            .pipe(multiselect_filter, 'loan', emprestimo_selecao)
            .pipe(multiselect_filter, 'contact', contato_selecao)
            .pipe(multiselect_filter, 'month', mes_selecao) 
            .pipe(multiselect_filter, 'day_of_week', dia_da_semana_selecao))

        # Mostra a tabela com os filtros aplicados
        st.subheader('Dados Filtrados')
        # Contagem de linhas do dataframe base filtrada sem o cabeçalho
        st.write(f"Total de linhas: {base_filtrada.shape[0]}")
        st.write(base_filtrada)

        # Verifica se a quantidade de linhas da base filtrada é menor que a base original
        if base_filtrada.shape[0] < base_real.shape[0]:
            # Cria um link para download da base filtrada
            excel_data_1 = base_filtrada
            excel_href_1 = download_excel(excel_data_1, 'base_filtrada')
            st.markdown(excel_href_1, unsafe_allow_html=True)
    
        st.markdown("---")
        st.subheader('Proporção de Aceitação')
        col1, col2 = st.columns(2)

        # Seleção do tipo de gráfico
        if tipo_grafico == 'Barras':
            # Gráfico da base original
            fig_real = px.bar(base_real['y'].value_counts(), title='Dados Originais')
            fig_real.update_layout(showlegend=False)
            fig_real.update_xaxes(title_text='')
            fig_real.update_yaxes(title_text='')
            col1.plotly_chart(fig_real)

            # Gráfico da base filtrada
            contagem_filtrada = base_filtrada['y'].value_counts()
            nao_primeiro = contagem_filtrada.reindex(index=['no'] + contagem_filtrada.index.difference(['no']).tolist())
            fig_filtrada = px.bar(nao_primeiro, title='Dados Filtrados')
            fig_filtrada.update_layout(showlegend=False)
            fig_filtrada.update_xaxes(title_text='')
            fig_filtrada.update_yaxes(title_text='')
            col2.plotly_chart(fig_filtrada)

        else:
            # Gráfico de pizza da base real
            contagem_base_real = base_real['y'].value_counts()
            nao_real_primeiro = contagem_base_real.reindex(index=['no'] + contagem_base_real.index.difference(['no']).tolist())
            fig_real = px.pie(nao_real_primeiro, title='Dados Originais', values = nao_real_primeiro)
            fig_real.update_layout(showlegend=False)
            fig_real.update_xaxes(title_text='')
            fig_real.update_yaxes(title_text='')
            col1.plotly_chart(fig_real)

            # Gráfico de pizza da base filtrada
            contagem_filtrada = base_filtrada['y'].value_counts()
            nao_primeiro = contagem_filtrada.reindex(index=['no'] + contagem_filtrada.index.difference(['no']).tolist())
            fig_filtrada = px.pie(nao_primeiro, title='Dados Filtrados', values = nao_primeiro)
            fig_filtrada.update_layout(showlegend=True)
            fig_filtrada.update_xaxes(title_text='')
            fig_filtrada.update_yaxes(title_text='')
            col2.plotly_chart(fig_filtrada)    

        # Mostra a contagem dos dados originais
        col1.write('Contagem dos Dados Originais')
        contagem_dados_originais = base_real['y'].value_counts()
        col1.write(contagem_dados_originais)

        # Cria um link de download para a contagem dos dados originais em formato Excel
        excel_data_2 = contagem_dados_originais.to_frame(name='Contagem')
        excel_href_2 = download_excel(excel_data_2, 'contagem_dados_originais')
        col1.markdown(excel_href_2, unsafe_allow_html=True)

        # Contagem da base filtrada
        col2.write("Contagem dos Dados Filtrados:")
        contagem_filtrada = base_filtrada['y'].value_counts()
        nao_primeiro = contagem_filtrada.reindex(index=['no'] + contagem_filtrada.index.difference(['no']).tolist())
        col2.write(nao_primeiro)

        # Cria um link de download para a contagem dos dados filtrados
        excel_data_3 = nao_primeiro.to_frame(name='Contagem')
        excel_href_3 = download_excel(excel_data_3, 'contagem_dados_filtrados')
        col2.markdown(excel_href_3, unsafe_allow_html=True)
else:
    st.subheader('Faça o upload da base de dados.')