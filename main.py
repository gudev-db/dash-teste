# dashboard.py - Versão Corrigida (Trecho dos KPIs)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Performance - Tráfego Pago",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================
# 1. CARREGAR DADOS DO CSV
# =====================

@st.cache_data
def carregar_dados():
    """Carrega os dados do arquivo CSV"""
    try:
        if os.path.exists('dados_trafego_pago.csv'):
            df = pd.read_csv('dados_trafego_pago.csv', encoding='utf-8')
            df['data'] = pd.to_datetime(df['data'])
            return df
        else:
            st.error("❌ Arquivo 'dados_trafego_pago.csv' não encontrado!")
            st.info("Execute o arquivo 'gerar_dados.py' primeiro para criar os dados.")
            return None
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return None

# =====================
# 2. FUNÇÕES DE ANÁLISE
# =====================

def calcular_metricas_periodo(df, data_inicio, data_fim):
    """Calcula métricas agregadas para o período"""
    df_periodo = df[(df['data'] >= data_inicio) & (df['data'] <= data_fim)]
    
    metricas = {
        'investimento': df_periodo['investimento'].sum(),
        'leads': df_periodo['leads'].sum(),
        'inscritos': df_periodo['inscritos'].sum(),
        'matriculas': df_periodo['matriculas'].sum(),
        'meta_investimento': df_periodo['meta_investimento'].sum(),
        'meta_leads': df_periodo['meta_leads'].sum(),
        'meta_inscritos': df_periodo['meta_inscritos'].sum(),
        'meta_matriculas': df_periodo['meta_matriculas'].sum(),
    }
    
    # Calcular custos
    metricas['cpl'] = metricas['investimento'] / metricas['leads'] if metricas['leads'] > 0 else 0
    metricas['cpi'] = metricas['investimento'] / metricas['inscritos'] if metricas['inscritos'] > 0 else 0
    metricas['cpmat'] = metricas['investimento'] / metricas['matriculas'] if metricas['matriculas'] > 0 else 0
    
    # Calcular taxas
    metricas['taxa_lead_inscrito'] = metricas['inscritos'] / metricas['leads'] if metricas['leads'] > 0 else 0
    metricas['taxa_inscrito_matricula'] = metricas['matriculas'] / metricas['inscritos'] if metricas['inscritos'] > 0 else 0
    metricas['taxa_lead_matricula'] = metricas['matriculas'] / metricas['leads'] if metricas['leads'] > 0 else 0
    
    return metricas

def calcular_atingimento(realizado, meta):
    """Calcula percentual de atingimento"""
    if meta > 0:
        return (realizado / meta) * 100
    return 0

def formatar_metricas_kpi(df_filtrado):
    """Formata métricas para exibição nos KPIs"""
    total_investimento = df_filtrado['investimento'].sum()
    total_meta_investimento = df_filtrado['meta_investimento'].sum()
    total_leads = df_filtrado['leads'].sum()
    total_meta_leads = df_filtrado['meta_leads'].sum()
    total_inscritos = df_filtrado['inscritos'].sum()
    total_meta_inscritos = df_filtrado['meta_inscritos'].sum()
    total_matriculas = df_filtrado['matriculas'].sum()
    total_meta_matriculas = df_filtrado['meta_matriculas'].sum()
    
    return {
        'investimento': {'realizado': total_investimento, 'meta': total_meta_investimento},
        'leads': {'realizado': total_leads, 'meta': total_meta_leads},
        'inscritos': {'realizado': total_inscritos, 'meta': total_meta_inscritos},
        'matriculas': {'realizado': total_matriculas, 'meta': total_meta_matriculas}
    }

# =====================
# 3. INTERFACE DO DASHBOARD
# =====================

# Carregar dados
df = carregar_dados()

if df is not None:
    # Sidebar - Filtros
    st.sidebar.title("🎯 Filtros")
    st.sidebar.markdown("---")
    
    # Período
    min_date = df['data'].min()
    max_date = df['data'].max()
    periodo = st.sidebar.date_input(
        "📅 Período",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    st.sidebar.markdown("---")
    
    # Marca
    marcas = ['Todas'] + sorted(df['marca'].unique().tolist())
    marca_selecionada = st.sidebar.selectbox("🏢 Marca", marcas)
    
    # Modalidade
    modalidades = ['Todas'] + sorted(df['modalidade'].unique().tolist())
    modalidade_selecionada = st.sidebar.selectbox("📚 Modalidade", modalidades)
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Dica:** Use os filtros para analisar períodos específicos ou comparar marcas e modalidades.")
    
    # Aplicar filtros
    df_filtrado = df.copy()
    if len(periodo) == 2:
        df_filtrado = df_filtrado[(df_filtrado['data'] >= pd.to_datetime(periodo[0])) & 
                                  (df_filtrado['data'] <= pd.to_datetime(periodo[1]))]
    if marca_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['marca'] == marca_selecionada]
    if modalidade_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['modalidade'] == modalidade_selecionada]
    
    # Calcular métricas do período
    metricas = calcular_metricas_periodo(df_filtrado, pd.to_datetime(periodo[0]), pd.to_datetime(periodo[1]))
    
    # Título
    st.title("📈 Dashboard de Performance - Tráfego Pago")
    st.markdown(f"*Período analisado: {periodo[0].strftime('%d/%m/%Y')} a {periodo[1].strftime('%d/%m/%Y')}*")
    st.markdown("---")
    
    # =====================
    # 4. VISÃO GERAL - COM META REAL (CORRIGIDO)
    # =====================
    
    st.header("📊 Visão Geral - Realizado vs Meta")
    
    # Calcular dados para KPIs
    kpis = formatar_metricas_kpi(df_filtrado)
    
    # Layout em 2 colunas para cada métrica
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Investimento")
        investimento_ating = calcular_atingimento(kpis['investimento']['realizado'], kpis['investimento']['meta'])
        diferenca_invest = kpis['investimento']['meta'] - kpis['investimento']['realizado']
        
        col1a, col1b = st.columns(2)
        with col1a:
            st.metric(
                "Realizado",
                f"R$ {kpis['investimento']['realizado']:,.0f}"
            )
        with col1b:
            # CORREÇÃO: Mostrar claramente o percentual da meta
            if investimento_ating >= 100:
                st.metric(
                    "Meta",
                    f"R$ {kpis['investimento']['meta']:,.0f}",
                    f"✅ {investimento_ating:.1f}% da meta (meta superada!)"
                )
            else:
                st.metric(
                    "Meta",
                    f"R$ {kpis['investimento']['meta']:,.0f}",
                    f"📊 {investimento_ating:.1f}% da meta (faltam R$ {diferenca_invest:,.0f})"
                )
    
    with col2:
        st.subheader("👥 Leads")
        leads_ating = calcular_atingimento(kpis['leads']['realizado'], kpis['leads']['meta'])
        diferenca_leads = kpis['leads']['meta'] - kpis['leads']['realizado']
        
        col2a, col2b = st.columns(2)
        with col2a:
            st.metric(
                "Realizado",
                f"{kpis['leads']['realizado']:,.0f}"
            )
        with col2b:
            if leads_ating >= 100:
                st.metric(
                    "Meta",
                    f"{kpis['leads']['meta']:,.0f}",
                    f"✅ {leads_ating:.1f}% da meta (meta superada!)"
                )
            else:
                st.metric(
                    "Meta",
                    f"{kpis['leads']['meta']:,.0f}",
                    f"📊 {leads_ating:.1f}% da meta (faltam {diferenca_leads:,.0f})"
                )
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("📝 Inscritos")
        inscritos_ating = calcular_atingimento(kpis['inscritos']['realizado'], kpis['inscritos']['meta'])
        diferenca_inscritos = kpis['inscritos']['meta'] - kpis['inscritos']['realizado']
        
        col3a, col3b = st.columns(2)
        with col3a:
            st.metric(
                "Realizado",
                f"{kpis['inscritos']['realizado']:,.0f}"
            )
        with col3b:
            if inscritos_ating >= 100:
                st.metric(
                    "Meta",
                    f"{kpis['inscritos']['meta']:,.0f}",
                    f"✅ {inscritos_ating:.1f}% da meta (meta superada!)"
                )
            else:
                st.metric(
                    "Meta",
                    f"{kpis['inscritos']['meta']:,.0f}",
                    f"📊 {inscritos_ating:.1f}% da meta (faltam {diferenca_inscritos:,.0f})"
                )
    
    with col4:
        st.subheader("🎓 Matrículas")
        matriculas_ating = calcular_atingimento(kpis['matriculas']['realizado'], kpis['matriculas']['meta'])
        diferenca_matriculas = kpis['matriculas']['meta'] - kpis['matriculas']['realizado']
        
        col4a, col4b = st.columns(2)
        with col4a:
            st.metric(
                "Realizado",
                f"{kpis['matriculas']['realizado']:,.0f}"
            )
        with col4b:
            if matriculas_ating >= 100:
                st.metric(
                    "Meta",
                    f"{kpis['matriculas']['meta']:,.0f}",
                    f"✅ {matriculas_ating:.1f}% da meta (meta superada!)"
                )
            else:
                st.metric(
                    "Meta",
                    f"{kpis['matriculas']['meta']:,.0f}",
                    f"📊 {matriculas_ating:.1f}% da meta (faltam {diferenca_matriculas:,.0f})"
                )
    
    st.markdown("---")
    
    # Gráfico de evolução mensal com meta
    st.subheader("📈 Evolução Mensal vs Meta")
    
    df_mensal = df_filtrado.groupby('data').agg({
        'investimento': 'sum',
        'leads': 'sum',
        'inscritos': 'sum',
        'matriculas': 'sum',
        'meta_investimento': 'sum',
        'meta_leads': 'sum',
        'meta_inscritos': 'sum',
        'meta_matriculas': 'sum'
    }).reset_index()
    
    # Selecionar métrica para visualização
    col_metric, col_empty = st.columns([1, 3])
    with col_metric:
        metrica_evolucao = st.selectbox(
            "Selecione a métrica:",
            ['investimento', 'leads', 'inscritos', 'matriculas']
        )
    
    nome_metrica = {
        'investimento': 'Investimento (R$)',
        'leads': 'Leads',
        'inscritos': 'Inscritos',
        'matriculas': 'Matrículas'
    }
    
    meta_col = f'meta_{metrica_evolucao}'
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_mensal['data'],
        y=df_mensal[metrica_evolucao],
        name='Realizado',
        marker_color='#1f77b4'
    ))
    fig.add_trace(go.Scatter(
        x=df_mensal['data'],
        y=df_mensal[meta_col],
        name='Meta',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title=f'Evolução Mensal - {nome_metrica[metrica_evolucao]}',
        yaxis_title=nome_metrica[metrica_evolucao],
        height=400,
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Métricas por Marca com metas (CORRIGIDO)
    st.subheader("🏢 Métricas por Marca - Realizado vs Meta")
    
    df_marca = df_filtrado.groupby('marca').agg({
        'investimento': 'sum',
        'leads': 'sum',
        'inscritos': 'sum',
        'matriculas': 'sum',
        'meta_investimento': 'sum',
        'meta_leads': 'sum',
        'meta_inscritos': 'sum',
        'meta_matriculas': 'sum'
    }).reset_index()
    
    for _, row in df_marca.iterrows():
        with st.expander(f"📌 {row['marca']}"):
            cpl = row['investimento'] / row['leads'] if row['leads'] > 0 else 0
            cpi = row['investimento'] / row['inscritos'] if row['inscritos'] > 0 else 0
            cpmat = row['investimento'] / row['matriculas'] if row['matriculas'] > 0 else 0
            
            ating_invest = calcular_atingimento(row['investimento'], row['meta_investimento'])
            ating_leads = calcular_atingimento(row['leads'], row['meta_leads'])
            ating_inscritos = calcular_atingimento(row['inscritos'], row['meta_inscritos'])
            ating_matriculas = calcular_atingimento(row['matriculas'], row['meta_matriculas'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                if ating_invest >= 100:
                    st.metric(
                        "💰 Investimento",
                        f"R$ {row['investimento']:,.0f}",
                        f"Meta: R$ {row['meta_investimento']:,.0f} (✅ {ating_invest:.1f}%)"
                    )
                else:
                    st.metric(
                        "💰 Investimento",
                        f"R$ {row['investimento']:,.0f}",
                        f"Meta: R$ {row['meta_investimento']:,.0f} (📊 {ating_invest:.1f}%)"
                    )
                
                if ating_leads >= 100:
                    st.metric(
                        "👥 Leads",
                        f"{row['leads']:,.0f}",
                        f"Meta: {row['meta_leads']:,.0f} (✅ {ating_leads:.1f}%)"
                    )
                else:
                    st.metric(
                        "👥 Leads",
                        f"{row['leads']:,.0f}",
                        f"Meta: {row['meta_leads']:,.0f} (📊 {ating_leads:.1f}%)"
                    )
            
            with col2:
                if ating_inscritos >= 100:
                    st.metric(
                        "📝 Inscritos",
                        f"{row['inscritos']:,.0f}",
                        f"Meta: {row['meta_inscritos']:,.0f} (✅ {ating_inscritos:.1f}%)"
                    )
                else:
                    st.metric(
                        "📝 Inscritos",
                        f"{row['inscritos']:,.0f}",
                        f"Meta: {row['meta_inscritos']:,.0f} (📊 {ating_inscritos:.1f}%)"
                    )
                
                if ating_matriculas >= 100:
                    st.metric(
                        "🎓 Matrículas",
                        f"{row['matriculas']:,.0f}",
                        f"Meta: {row['meta_matriculas']:,.0f} (✅ {ating_matriculas:.1f}%)"
                    )
                else:
                    st.metric(
                        "🎓 Matrículas",
                        f"{row['matriculas']:,.0f}",
                        f"Meta: {row['meta_matriculas']:,.0f} (📊 {ating_matriculas:.1f}%)"
                    )
            
            # Custos
            st.write("**Custos:**")
            col3, col4, col5 = st.columns(3)
            col3.metric("CPL", f"R$ {cpl:.2f}")
            col4.metric("CPI", f"R$ {cpi:.2f}")
            col5.metric("CPMat", f"R$ {cpmat:.2f}")
    
    st.markdown("---")
    
    # =====================
    # 5. FUNIL DE CONVERSÃO
    # =====================
    
    st.header("🔄 Funil de Conversão")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Funil Consolidado")
        
        funil_data = pd.DataFrame({
            'Etapa': ['Investimento', 'Leads', 'Inscritos', 'Matrículas'],
            'Valor': [
                metricas['investimento'],
                metricas['leads'],
                metricas['inscritos'],
                metricas['matriculas']
            ],
            'Meta': [
                metricas['meta_investimento'],
                metricas['meta_leads'],
                metricas['meta_inscritos'],
                metricas['meta_matriculas']
            ]
        })
        
        fig_funil = go.Figure()
        fig_funil.add_trace(go.Funnel(
            y=funil_data['Etapa'],
            x=funil_data['Valor'],
            name='Realizado',
            textposition="inside",
            textinfo="value+percent previous",
            marker=dict(color=['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728'])
        ))
        fig_funil.update_layout(height=400)
        st.plotly_chart(fig_funil, use_container_width=True)
    
    with col2:
        st.subheader("Taxas de Conversão")
        
        if metricas['leads'] > 0:
            lead_inscrito = metricas['taxa_lead_inscrito'] * 100
            lead_matricula = metricas['taxa_lead_matricula'] * 100
            inscrito_matricula = metricas['taxa_inscrito_matricula'] * 100
            
            taxa_df = pd.DataFrame({
                'Conversão': ['Lead → Inscrito', 'Inscrito → Matrícula', 'Lead → Matrícula'],
                'Taxa (%)': [lead_inscrito, inscrito_matricula, lead_matricula]
            })
            
            fig_taxas = px.bar(
                taxa_df, 
                x='Conversão', 
                y='Taxa (%)', 
                color='Taxa (%)',
                text_auto='.1f',
                color_continuous_scale='Viridis'
            )
            fig_taxas.update_layout(height=400)
            st.plotly_chart(fig_taxas, use_container_width=True)
    
    # Custos por Etapa
    st.subheader("💰 Custos por Etapa")
    custos_df = pd.DataFrame({
        'Métrica': ['CPL', 'CPI', 'CPMat'],
        'Valor (R$)': [metricas['cpl'], metricas['cpi'], metricas['cpmat']]
    })
    fig_custos = px.bar(
        custos_df, 
        x='Métrica', 
        y='Valor (R$)',
        text_auto='.2f', 
        color='Métrica',
        color_discrete_sequence=['#1f77b4', '#ff7f0e', '#d62728']
    )
    fig_custos.update_layout(height=350)
    st.plotly_chart(fig_custos, use_container_width=True)
    
    st.markdown("---")
    
    # =====================
    # 6. COMPARATIVO ENTRE MARCAS
    # =====================
    
    st.header("🏢 Comparativo entre Marcas")
    
    df_comparativo = df_filtrado.groupby('marca').agg({
        'investimento': 'sum',
        'leads': 'sum',
        'inscritos': 'sum',
        'matriculas': 'sum',
        'meta_investimento': 'sum',
        'meta_leads': 'sum',
        'meta_inscritos': 'sum',
        'meta_matriculas': 'sum'
    }).reset_index()
    
    # Calcular métricas por marca
    for idx, row in df_comparativo.iterrows():
        df_comparativo.loc[idx, 'cpl'] = row['investimento'] / row['leads'] if row['leads'] > 0 else 0
        df_comparativo.loc[idx, 'cpi'] = row['investimento'] / row['inscritos'] if row['inscritos'] > 0 else 0
        df_comparativo.loc[idx, 'cpmat'] = row['investimento'] / row['matriculas'] if row['matriculas'] > 0 else 0
        df_comparativo.loc[idx, 'conversao'] = (row['matriculas'] / row['leads'] * 100) if row['leads'] > 0 else 0
        df_comparativo.loc[idx, 'atingimento_invest'] = (row['investimento'] / row['meta_investimento'] * 100) if row['meta_investimento'] > 0 else 0
        df_comparativo.loc[idx, 'atingimento_leads'] = (row['leads'] / row['meta_leads'] * 100) if row['meta_leads'] > 0 else 0
        df_comparativo.loc[idx, 'atingimento_matriculas'] = (row['matriculas'] / row['meta_matriculas'] * 100) if row['meta_matriculas'] > 0 else 0
    
    # Gráfico comparativo
    fig_comparativo = go.Figure()
    fig_comparativo.add_trace(go.Bar(
        x=df_comparativo['marca'],
        y=df_comparativo['leads'],
        name='Leads Realizado',
        marker_color='#2ca02c'
    ))
    fig_comparativo.add_trace(go.Bar(
        x=df_comparativo['marca'],
        y=df_comparativo['meta_leads'],
        name='Meta Leads',
        marker_color='#98df8a',
        opacity=0.7
    ))
    fig_comparativo.add_trace(go.Bar(
        x=df_comparativo['marca'],
        y=df_comparativo['matriculas'],
        name='Matrículas Realizado',
        marker_color='#d62728'
    ))
    fig_comparativo.add_trace(go.Bar(
        x=df_comparativo['marca'],
        y=df_comparativo['meta_matriculas'],
        name='Meta Matrículas',
        marker_color='#ff9896',
        opacity=0.7
    ))
    fig_comparativo.update_layout(
        title='Leads vs Matrículas - Realizado vs Meta',
        barmode='group',
        height=400
    )
    st.plotly_chart(fig_comparativo, use_container_width=True)
    
    # Tabela comparativa completa
    st.subheader("📊 Tabela Comparativa Detalhada")
    st.dataframe(
        df_comparativo.style.format({
            'investimento': 'R$ {:,.0f}',
            'meta_investimento': 'R$ {:,.0f}',
            'atingimento_invest': '{:.1f}%',
            'leads': '{:,.0f}',
            'meta_leads': '{:,.0f}',
            'atingimento_leads': '{:.1f}%',
            'inscritos': '{:,.0f}',
            'meta_inscritos': '{:,.0f}',
            'matriculas': '{:,.0f}',
            'meta_matriculas': '{:,.0f}',
            'atingimento_matriculas': '{:.1f}%',
            'cpl': 'R$ {:.2f}',
            'cpi': 'R$ {:.2f}',
            'cpmat': 'R$ {:.2f}',
            'conversao': '{:.1f}%'
        }),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # =====================
    # 7. ANÁLISE POR REGIÃO
    # =====================
    
    st.header("📍 Análise por Região")
    
    df_regiao = df_filtrado.groupby(['cidade', 'marca']).agg({
        'leads': 'sum',
        'matriculas': 'sum',
        'meta_leads': 'sum',
        'meta_matriculas': 'sum'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top cidades por leads
        top_leads = df_regiao.groupby('cidade')['leads'].sum().sort_values(ascending=False).head(10)
        fig_leads_cidade = px.bar(
            x=top_leads.values,
            y=top_leads.index,
            orientation='h',
            title='Top 10 Cidades por Leads',
            text_auto=True,
            color=top_leads.values,
            color_continuous_scale='Blues'
        )
        fig_leads_cidade.update_layout(height=400)
        st.plotly_chart(fig_leads_cidade, use_container_width=True)
    
    with col2:
        # Top cidades por matrículas
        top_matriculas = df_regiao.groupby('cidade')['matriculas'].sum().sort_values(ascending=False).head(10)
        fig_matriculas_cidade = px.bar(
            x=top_matriculas.values,
            y=top_matriculas.index,
            orientation='h',
            title='Top 10 Cidades por Matrículas',
            text_auto=True,
            color=top_matriculas.values,
            color_continuous_scale='Reds'
        )
        fig_matriculas_cidade.update_layout(height=400)
        st.plotly_chart(fig_matriculas_cidade, use_container_width=True)
    
    # Tabela por região
    st.subheader("📊 Detalhamento por Cidade")
    st.dataframe(
        df_regiao.sort_values('leads', ascending=False).head(20).style.format({
            'leads': '{:,.0f}',
            'matriculas': '{:,.0f}',
            'meta_leads': '{:,.0f}',
            'meta_matriculas': '{:,.0f}'
        }),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # =====================
    # 8. ANÁLISE POR CURSO
    # =====================
    
    st.header("📚 Análise por Curso")
    
    df_curso = df_filtrado.groupby(['curso', 'marca']).agg({
        'leads': 'sum',
        'matriculas': 'sum',
        'meta_leads': 'sum',
        'meta_matriculas': 'sum'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        top_cursos_leads = df_curso.groupby('curso')['leads'].sum().sort_values(ascending=False).head(10)
        fig_cursos_leads = px.bar(
            x=top_cursos_leads.values,
            y=top_cursos_leads.index,
            orientation='h',
            title='Top 10 Cursos por Leads',
            text_auto=True,
            color=top_cursos_leads.values,
            color_continuous_scale='Greens'
        )
        fig_cursos_leads.update_layout(height=400)
        st.plotly_chart(fig_cursos_leads, use_container_width=True)
    
    with col2:
        top_cursos_matriculas = df_curso.groupby('curso')['matriculas'].sum().sort_values(ascending=False).head(10)
        fig_cursos_matriculas = px.bar(
            x=top_cursos_matriculas.values,
            y=top_cursos_matriculas.index,
            orientation='h',
            title='Top 10 Cursos por Matrículas',
            text_auto=True,
            color=top_cursos_matriculas.values,
            color_continuous_scale='Oranges'
        )
        fig_cursos_matriculas.update_layout(height=400)
        st.plotly_chart(fig_cursos_matriculas, use_container_width=True)
    
    st.markdown("---")
    
    # =====================
    # 9. ANÁLISE POR PLATAFORMA
    # =====================
    
    st.header("📱 Análise por Plataforma")
    
    df_plataforma = df_filtrado.groupby(['plataforma', 'marca']).agg({
        'leads': 'sum',
        'matriculas': 'sum',
        'investimento': 'sum'
    }).reset_index()
    
    # Gráfico de leads por plataforma
    fig_plataforma = px.bar(
        df_plataforma,
        x='plataforma',
        y='leads',
        color='marca',
        title='Leads por Plataforma',
        barmode='group',
        text_auto=True
    )
    fig_plataforma.update_layout(height=400)
    st.plotly_chart(fig_plataforma, use_container_width=True)
    
    # Gráfico de matrículas por plataforma
    fig_plataforma_mat = px.bar(
        df_plataforma,
        x='plataforma',
        y='matriculas',
        color='marca',
        title='Matrículas por Plataforma',
        barmode='group',
        text_auto=True
    )
    fig_plataforma_mat.update_layout(height=400)
    st.plotly_chart(fig_plataforma_mat, use_container_width=True)
    
    # Métricas de plataforma
    df_plataforma_meta = df_plataforma[df_plataforma['plataforma'] == 'Meta']
    df_plataforma_google = df_plataforma[df_plataforma['plataforma'] == 'Google']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📘 Meta Ads")
        if not df_plataforma_meta.empty:
            for _, row in df_plataforma_meta.iterrows():
                cpl = row['investimento'] / row['leads'] if row['leads'] > 0 else 0
                cpmat = row['investimento'] / row['matriculas'] if row['matriculas'] > 0 else 0
                st.write(f"**{row['marca']}**")
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Leads", f"{row['leads']:,.0f}")
                col_b.metric("Matrículas", f"{row['matriculas']:,.0f}")
                col_c.metric("CPL", f"R$ {cpl:.2f}")
    
    with col2:
        st.subheader("📗 Google Ads")
        if not df_plataforma_google.empty:
            for _, row in df_plataforma_google.iterrows():
                cpl = row['investimento'] / row['leads'] if row['leads'] > 0 else 0
                cpmat = row['investimento'] / row['matriculas'] if row['matriculas'] > 0 else 0
                st.write(f"**{row['marca']}**")
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Leads", f"{row['leads']:,.0f}")
                col_b.metric("Matrículas", f"{row['matriculas']:,.0f}")
                col_c.metric("CPL", f"R$ {cpl:.2f}")
    
    st.markdown("---")
    
    # =====================
    # 10. ANÁLISE DE CAMPANHAS
    # =====================
    
    st.header("🎯 Análise de Campanhas")
    
    # Criativos do Meta
    df_meta = df_filtrado[df_filtrado['plataforma'] == 'Meta']
    if not df_meta.empty:
        st.subheader("🎨 Performance de Criativos - Meta")
        
        df_criativos = df_meta.groupby(['criativo', 'tipo_criativo']).agg({
            'leads': 'sum',
            'matriculas': 'sum',
            'investimento': 'sum',
            'impressoes': 'sum',
            'cliques': 'sum'
        }).reset_index()
        
        # Métricas por criativo
        for _, row in df_criativos.iterrows():
            if row['criativo']:
                cpl = row['investimento'] / row['leads'] if row['leads'] > 0 else 0
                cpmat = row['investimento'] / row['matriculas'] if row['matriculas'] > 0 else 0
                ctr = (row['cliques'] / row['impressoes'] * 100) if row['impressoes'] > 0 else 0
                
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns(6)
                    col1.metric(f"🎨 {row['criativo']}", f"{row['tipo_criativo']}")
                    col2.metric("Leads", f"{row['leads']:,.0f}")
                    col3.metric("Matrículas", f"{row['matriculas']:,.0f}")
                    col4.metric("CPL", f"R$ {cpl:.2f}")
                    col5.metric("CPMat", f"R$ {cpmat:.2f}")
                    col6.metric("CTR", f"{ctr:.1f}%")
                    st.markdown("---")
    
    # Termos de Pesquisa - Google
    df_google = df_filtrado[df_filtrado['plataforma'] == 'Google']
    if not df_google.empty:
        st.subheader("🔍 Termos de Pesquisa - Google")
        
        df_termos = df_google.groupby('termo_pesquisa').agg({
            'leads': 'sum',
            'matriculas': 'sum',
            'investimento': 'sum'
        }).reset_index()
        
        df_termos = df_termos[df_termos['termo_pesquisa'] != '']
        if not df_termos.empty:
            df_termos['cpl'] = df_termos['investimento'] / df_termos['leads']
            df_termos['cpmat'] = df_termos['investimento'] / df_termos['matriculas']
            
            st.dataframe(
                df_termos.sort_values('leads', ascending=False).head(10).style.format({
                    'investimento': 'R$ {:,.0f}',
                    'leads': '{:,.0f}',
                    'matriculas': '{:,.0f}',
                    'cpl': 'R$ {:.2f}',
                    'cpmat': 'R$ {:.2f}'
                }),
                use_container_width=True
            )
    
    # Inteligência de Comportamento
    st.subheader("🧠 Inteligência de Comportamento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Performance por dia da semana
        df_dia = df_filtrado.groupby('dia_semana').agg({
            'leads': 'sum',
            'matriculas': 'sum'
        }).reset_index()
        
        ordem_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        df_dia['dia_semana'] = pd.Categorical(df_dia['dia_semana'], categories=ordem_dias, ordered=True)
        df_dia = df_dia.sort_values('dia_semana')
        
        fig_dia = px.bar(
            df_dia, 
            x='dia_semana', 
            y='leads',
            title='Leads por Dia da Semana',
            text_auto=True,
            color='leads',
            color_continuous_scale='Blues'
        )
        fig_dia.update_layout(height=300)
        st.plotly_chart(fig_dia, use_container_width=True)
    
    with col2:
        # Performance por horário
        df_horario = df_filtrado.groupby('horario').agg({
            'leads': 'sum',
            'matriculas': 'sum'
        }).reset_index()
        
        fig_horario = px.bar(
            df_horario, 
            x='horario', 
            y='leads',
            title='Leads por Horário',
            text_auto=True,
            color='leads',
            color_continuous_scale='Greens'
        )
        fig_horario.update_layout(height=300)
        st.plotly_chart(fig_horario, use_container_width=True)
    
    # =====================
    # 11. INSIGHTS E DOCUMENTAÇÃO
    # =====================
    
    st.markdown("---")
    st.header("💡 Insights e Documentação")
    
    with st.expander("📌 Principais Insights do Dashboard"):
        st.markdown(f"""
        **1. Eficiência de Conversão**
        - Taxa de conversão Lead→Matrícula: **{metricas['taxa_lead_matricula']*100:.1f}%**
        - Custo por matrícula (CPMat): **R$ {metricas['cpmat']:.2f}**
        - Meta de matrículas: **{metricas['meta_matriculas']:,.0f}** vs Realizado: **{metricas['matriculas']:,.0f}**
        
        **2. Atingimento das Metas**
        - Investimento: **{calcular_atingimento(metricas['investimento'], metricas['meta_investimento']):.1f}%** da meta
        - Leads: **{calcular_atingimento(metricas['leads'], metricas['meta_leads']):.1f}%** da meta
        - Inscritos: **{calcular_atingimento(metricas['inscritos'], metricas['meta_inscritos']):.1f}%** da meta
        - Matrículas: **{calcular_atingimento(metricas['matriculas'], metricas['meta_matriculas']):.1f}%** da meta
        
        **3. Performance por Marca**
        - Marca 1: Maior volume de leads, mas custo mais alto
        - Marca 2: Menor volume, mas mais eficiente em conversão
        
        **4. Sazonalidade**
        - Picos de conversão em março e agosto
        - Recomendação: Aumentar investimento em 15% nesses períodos
        
        **5. Otimização de Campanhas**
        - Criativos "Fundo" têm melhor conversão
        - Melhor horário: Tarde/Noite
        - Melhor dia: Terça/Quarta
        """)
    
    with st.expander("📖 Documentação Técnica"):
        st.markdown("""
        ### Estrutura dos Dados
        
        **Granularidade:** Mensal
        **Período:** Últimos 12 meses
        **Dimensões:** Marca, Modalidade, Plataforma, Região, Curso
        
        ### Métricas Calculadas
        
        - **CPL** = Investimento / Leads
        - **CPI** = Investimento / Inscritos
        - **CPMat** = Investimento / Matrículas
        - **Taxa L→I** = Inscritos / Leads
        - **Taxa I→M** = Matrículas / Inscritos
        - **Taxa L→M** = Matrículas / Leads
        - **Atingimento** = (Realizado / Meta) × 100
        
        ### Filtros Disponíveis
        
        - ✅ Período (Data Inicial e Final)
        - ✅ Marca (Marca 1, Marca 2)
        - ✅ Modalidade (Presencial, EAD)
        
        ### Premissas dos Dados Simulados
        
        1. Dados gerados com distribuição realista
        2. Sazonalidade considerada (picos em março/agosto)
        3. Correlações entre métricas mantidas
        4. Metas calculadas com variação independente (-10% a +35%)
        5. Matrículas < Inscritos < Leads (funil consistente)
        6. CPMat > CPI > CPL (custos crescentes)
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("**Dashboard desenvolvido para o Processo Seletivo - Agência de Tráfego Pago**")
    st.markdown(f"*Dados atualizados até {datetime.now().strftime('%d/%m/%Y')}*")
    st.markdown(f"*Total de registros carregados: {len(df):,}*")

else:
    st.warning("⚠️ Não foi possível carregar os dados. Verifique se o arquivo CSV foi gerado corretamente.")
