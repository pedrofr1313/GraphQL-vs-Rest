"""
Dashboard Interativo: Análise REST vs GraphQL
Disciplina: Laboratório de Experimentação de Software

Este dashboard permite visualizar e analisar os dados do experimento,
respondendo às questões de pesquisa RQ1 (tempo de resposta) e RQ2 (tamanho da resposta).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy import stats
from scipy.stats import shapiro, ttest_rel, wilcoxon
import os

# Configuração da página
st.set_page_config(
    page_title="REST vs GraphQL - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cores consistentes para REST e GraphQL
COLORS = {
    'REST': '#1f77b4',      # Azul
    'GraphQL': '#ff7f0e'    # Laranja
}

# Carregar dados
@st.cache_data
def load_data():
    """Carrega os dados do experimento do arquivo CSV."""
    csv_path = os.path.join(os.path.dirname(__file__), 'experiment_results.csv')
    if not os.path.exists(csv_path):
        st.error(f"Arquivo não encontrado: {csv_path}")
        return None
    df = pd.read_csv(csv_path)
    return df

# Funções de análise estatística
def test_normality(data):
    """Testa normalidade usando Shapiro-Wilk."""
    stat, p_value = shapiro(data)
    return stat, p_value, p_value > 0.05

def cohens_d(x, y):
    """Calcula o tamanho do efeito (Cohen's d) para amostras pareadas."""
    diff = x - y
    d = diff.mean() / diff.std()
    return d

def interpret_cohens_d(d):
    """Interpreta o tamanho do efeito de Cohen."""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "Desprezível"
    elif abs_d < 0.5:
        return "Pequeno"
    elif abs_d < 0.8:
        return "Médio"
    else:
        return "Grande"

def perform_statistical_test(rest_data, graphql_data):
    """
    Realiza testes estatísticos apropriados.
    Retorna resultados do teste de normalidade e do teste de hipótese.
    """
    # Teste de normalidade nas diferenças
    differences = rest_data - graphql_data
    shapiro_stat, shapiro_p, is_normal = test_normality(differences)
    
    # Escolher teste apropriado
    if is_normal:
        # Teste t pareado
        t_stat, t_p = ttest_rel(rest_data, graphql_data)
        test_name = "Teste t pareado"
        test_stat = t_stat
        test_p = t_p
    else:
        # Teste de Wilcoxon (não-paramétrico)
        w_stat, w_p = wilcoxon(rest_data, graphql_data)
        test_name = "Teste de Wilcoxon"
        test_stat = w_stat
        test_p = w_p
    
    # Calcular Cohen's d
    d = cohens_d(rest_data, graphql_data)
    d_interpretation = interpret_cohens_d(d)
    
    # Intervalo de confiança da diferença (95%)
    diff_mean = differences.mean()
    diff_std = differences.std()
    n = len(differences)
    se = diff_std / np.sqrt(n)
    ci_lower = diff_mean - 1.96 * se
    ci_upper = diff_mean + 1.96 * se
    
    return {
        'shapiro_stat': shapiro_stat,
        'shapiro_p': shapiro_p,
        'is_normal': is_normal,
        'test_name': test_name,
        'test_stat': test_stat,
        'test_p': test_p,
        'cohens_d': d,
        'd_interpretation': d_interpretation,
        'diff_mean': diff_mean,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper
    }

def create_comparison_boxplot(df, metric_col, metric_label):
    """Cria box plot comparativo."""
    fig = px.box(
        df,
        x='type',
        y=metric_col,
        color='type',
        color_discrete_map=COLORS,
        title=f'Distribuição de {metric_label}',
        labels={metric_col: metric_label, 'type': 'Tipo de API'}
    )
    fig.update_layout(
        showlegend=False,
        height=400,
        template='plotly_white'
    )
    return fig

def create_histogram_comparison(df, metric_col, metric_label):
    """Cria histograma comparativo."""
    fig = go.Figure()
    
    for api_type in ['REST', 'GraphQL']:
        data = df[df['type'] == api_type][metric_col]
        fig.add_trace(go.Histogram(
            x=data,
            name=api_type,
            marker_color=COLORS[api_type],
            opacity=0.7,
            nbinsx=20
        ))
    
    fig.update_layout(
        title=f'Distribuição de {metric_label}',
        xaxis_title=metric_label,
        yaxis_title='Frequência',
        barmode='overlay',
        height=400,
        template='plotly_white',
        legend=dict(x=0.7, y=0.95)
    )
    return fig

def create_line_plot_by_id(df, metric_col, metric_label):
    """Cria gráfico de linha mostrando valores por ID."""
    fig = go.Figure()
    
    for api_type in ['REST', 'GraphQL']:
        data = df[df['type'] == api_type].sort_values('id')
        fig.add_trace(go.Scatter(
            x=data['id'],
            y=data[metric_col],
            mode='lines+markers',
            name=api_type,
            line=dict(color=COLORS[api_type], width=2),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title=f'{metric_label} por ID do Personagem',
        xaxis_title='ID do Personagem',
        yaxis_title=metric_label,
        height=400,
        template='plotly_white',
        hovermode='x unified'
    )
    return fig

def create_scatter_comparison(df, metric_col, metric_label):
    """Cria scatter plot comparando REST vs GraphQL por ID."""
    rest_data = df[df['type'] == 'REST'].sort_values('id')
    graphql_data = df[df['type'] == 'GraphQL'].sort_values('id')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=rest_data[metric_col],
        y=graphql_data[metric_col],
        mode='markers',
        marker=dict(
            size=10,
            color=rest_data['id'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='ID')
        ),
        text=rest_data['id'],
        hovertemplate='ID: %{text}<br>REST: %{x:.2f}<br>GraphQL: %{y:.2f}<extra></extra>',
        name='Comparação'
    ))
    
    # Linha de igualdade
    min_val = min(rest_data[metric_col].min(), graphql_data[metric_col].min())
    max_val = max(rest_data[metric_col].max(), graphql_data[metric_col].max())
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        line=dict(dash='dash', color='gray'),
        name='Linha de Igualdade',
        showlegend=False
    ))
    
    fig.update_layout(
        title=f'Comparação {metric_label}: REST vs GraphQL',
        xaxis_title=f'REST - {metric_label}',
        yaxis_title=f'GraphQL - {metric_label}',
        height=500,
        template='plotly_white'
    )
    return fig

def create_bar_comparison(df, metric_col, metric_label):
    """Cria gráfico de barras comparativo."""
    summary = df.groupby('type')[metric_col].agg(['mean', 'median', 'std']).reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=summary['type'],
        y=summary['mean'],
        name='Média',
        marker_color=[COLORS[t] for t in summary['type']],
        error_y=dict(type='data', array=summary['std']),
        text=[f"{v:.2f}" for v in summary['mean']],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=f'Média de {metric_label} com Desvio Padrão',
        xaxis_title='Tipo de API',
        yaxis_title=metric_label,
        height=400,
        template='plotly_white',
        showlegend=False
    )
    return fig

# Carregar dados
df = load_data()

if df is not None:
    # Sidebar - Navegação
    st.sidebar.title("📊 Dashboard REST vs GraphQL")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navegação",
        ["Visão Geral", "Análise de Tempo (RQ1)", "Análise de Tamanho (RQ2)", "Análise Detalhada"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Informações do Dataset")
    st.sidebar.metric("Total de Registros", len(df))
    st.sidebar.metric("Personagens Únicos", df['id'].nunique())
    st.sidebar.metric("Requisições REST", len(df[df['type'] == 'REST']))
    st.sidebar.metric("Requisições GraphQL", len(df[df['type'] == 'GraphQL']))
    
    # Separar dados por tipo
    rest_df = df[df['type'] == 'REST'].copy()
    graphql_df = df[df['type'] == 'GraphQL'].copy()
    
    # PÁGINA 1: VISÃO GERAL
    if page == "Visão Geral":
        st.title("📊 Visão Geral do Experimento")
        st.markdown("---")
        
        # Cards de métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Tempo Médio REST",
                f"{rest_df['time_ms'].mean():.2f} ms",
                delta=f"vs GraphQL: {rest_df['time_ms'].mean() - graphql_df['time_ms'].mean():.2f} ms"
            )
        
        with col2:
            st.metric(
                "Tempo Médio GraphQL",
                f"{graphql_df['time_ms'].mean():.2f} ms",
                delta=f"vs REST: {graphql_df['time_ms'].mean() - rest_df['time_ms'].mean():.2f} ms"
            )
        
        with col3:
            st.metric(
                "Tamanho Médio REST",
                f"{rest_df['size_bytes'].mean():.0f} bytes",
                delta=f"vs GraphQL: {rest_df['size_bytes'].mean() - graphql_df['size_bytes'].mean():.0f} bytes"
            )
        
        with col4:
            st.metric(
                "Tamanho Médio GraphQL",
                f"{graphql_df['size_bytes'].mean():.0f} bytes",
                delta=f"vs REST: {graphql_df['size_bytes'].mean() - rest_df['size_bytes'].mean():.0f} bytes"
            )
        
        st.markdown("---")
        
        # Gráficos comparativos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Tempo de Resposta")
            fig_time = create_comparison_boxplot(df, 'time_ms', 'Tempo de Resposta (ms)')
            st.plotly_chart(fig_time, use_container_width=True)
        
        with col2:
            st.subheader("📦 Tamanho da Resposta")
            fig_size = create_comparison_boxplot(df, 'size_bytes', 'Tamanho da Resposta (bytes)')
            st.plotly_chart(fig_size, use_container_width=True)
        
        # Tabela resumo estatístico
        st.markdown("---")
        st.subheader("📋 Resumo Estatístico")
        
        summary_data = {
            'Métrica': ['Tempo (ms)', 'Tempo (ms)', 'Tamanho (bytes)', 'Tamanho (bytes)'],
            'Tipo': ['REST', 'GraphQL', 'REST', 'GraphQL'],
            'Média': [
                rest_df['time_ms'].mean(),
                graphql_df['time_ms'].mean(),
                rest_df['size_bytes'].mean(),
                graphql_df['size_bytes'].mean()
            ],
            'Mediana': [
                rest_df['time_ms'].median(),
                graphql_df['time_ms'].median(),
                rest_df['size_bytes'].median(),
                graphql_df['size_bytes'].median()
            ],
            'Desvio Padrão': [
                rest_df['time_ms'].std(),
                graphql_df['time_ms'].std(),
                rest_df['size_bytes'].std(),
                graphql_df['size_bytes'].std()
            ],
            'Mínimo': [
                rest_df['time_ms'].min(),
                graphql_df['time_ms'].min(),
                rest_df['size_bytes'].min(),
                graphql_df['size_bytes'].min()
            ],
            'Máximo': [
                rest_df['time_ms'].max(),
                graphql_df['time_ms'].max(),
                rest_df['size_bytes'].max(),
                graphql_df['size_bytes'].max()
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # PÁGINA 2: ANÁLISE DE TEMPO (RQ1)
    elif page == "Análise de Tempo (RQ1)":
        st.title("⏱️ Análise de Tempo de Resposta (RQ1)")
        st.markdown("**Questão de Pesquisa:** As requisições realizadas por meio de GraphQL apresentam tempo de resposta inferior ao de requisições REST equivalentes?")
        st.markdown("---")
        
        # Alinhar dados por ID para análise pareada
        rest_sorted = rest_df.sort_values('id')['time_ms'].values
        graphql_sorted = graphql_df.sort_values('id')['time_ms'].values
        
        # Testes estatísticos
        test_results = perform_statistical_test(rest_sorted, graphql_sorted)
        
        # Cards com resultados principais
        col1, col2, col3 = st.columns(3)
        
        with col1:
            diff = test_results['diff_mean']
            st.metric(
                "Diferença Média",
                f"{diff:.2f} ms",
                delta="REST - GraphQL"
            )
        
        with col2:
            ci_lower = test_results['ci_lower']
            ci_upper = test_results['ci_upper']
            st.metric(
                "IC 95%",
                f"[{ci_lower:.2f}, {ci_upper:.2f}] ms"
            )
        
        with col3:
            d = test_results['cohens_d']
            st.metric(
                "Tamanho do Efeito (Cohen's d)",
                f"{d:.3f}",
                delta=test_results['d_interpretation']
            )
        
        st.markdown("---")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Histograma Comparativo")
            fig_hist = create_histogram_comparison(df, 'time_ms', 'Tempo de Resposta (ms)')
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            st.subheader("📈 Box Plot")
            fig_box = create_comparison_boxplot(df, 'time_ms', 'Tempo de Resposta (ms)')
            st.plotly_chart(fig_box, use_container_width=True)
        
        st.subheader("📉 Tempo de Resposta por ID")
        fig_line = create_line_plot_by_id(df, 'time_ms', 'Tempo de Resposta (ms)')
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Resultados dos testes estatísticos
        st.markdown("---")
        st.subheader("🔬 Resultados dos Testes Estatísticos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Teste de Normalidade (Shapiro-Wilk)")
            st.write(f"**Estatística:** {test_results['shapiro_stat']:.4f}")
            st.write(f"**p-valor:** {test_results['shapiro_p']:.4f}")
            if test_results['is_normal']:
                st.success("✅ Dados seguem distribuição normal (p > 0.05)")
            else:
                st.warning("⚠️ Dados não seguem distribuição normal (p ≤ 0.05)")
        
        with col2:
            st.markdown(f"##### {test_results['test_name']}")
            st.write(f"**Estatística:** {test_results['test_stat']:.4f}")
            st.write(f"**p-valor:** {test_results['test_p']:.4f}")
            
            alpha = 0.05
            if test_results['test_p'] < alpha:
                st.success(f"✅ Diferença estatisticamente significativa (p < {alpha})")
                if diff < 0:
                    st.info("📊 REST é **mais rápido** que GraphQL")
                else:
                    st.info("📊 GraphQL é **mais rápido** que REST")
            else:
                st.warning(f"⚠️ Diferença não estatisticamente significativa (p ≥ {alpha})")
        
        # Interpretação
        st.markdown("---")
        st.subheader("💡 Interpretação dos Resultados")
        
        interpretation = f"""
        **Hipótese Nula (H₀):** μ_GraphQL ≥ μ_REST  
        **Hipótese Alternativa (H₁):** μ_GraphQL < μ_REST
        
        - **Diferença média:** {diff:.2f} ms (REST - GraphQL)
        - **Teste utilizado:** {test_results['test_name']}
        - **Tamanho do efeito:** {d:.3f} ({test_results['d_interpretation']})
        - **Intervalo de confiança 95%:** [{ci_lower:.2f}, {ci_upper:.2f}] ms
        
        """
        
        if test_results['test_p'] < 0.05:
            if diff < 0:
                interpretation += "**Conclusão:** Rejeitamos H₀. REST apresenta tempo de resposta **significativamente menor** que GraphQL."
            else:
                interpretation += "**Conclusão:** Rejeitamos H₀. GraphQL apresenta tempo de resposta **significativamente menor** que REST."
        else:
            interpretation += "**Conclusão:** Não rejeitamos H₀. Não há evidência suficiente de diferença significativa entre os tempos de resposta."
        
        st.markdown(interpretation)
    
    # PÁGINA 3: ANÁLISE DE TAMANHO (RQ2)
    elif page == "Análise de Tamanho (RQ2)":
        st.title("📦 Análise de Tamanho da Resposta (RQ2)")
        st.markdown("**Questão de Pesquisa:** O tamanho das respostas retornadas por GraphQL é menor do que o tamanho das respostas retornadas por REST?")
        st.markdown("---")
        
        # Alinhar dados por ID para análise pareada
        rest_sorted = rest_df.sort_values('id')['size_bytes'].values
        graphql_sorted = graphql_df.sort_values('id')['size_bytes'].values
        
        # Testes estatísticos
        test_results = perform_statistical_test(rest_sorted, graphql_sorted)
        
        # Cards com resultados principais
        col1, col2, col3 = st.columns(3)
        
        with col1:
            diff = test_results['diff_mean']
            reduction_pct = (diff / rest_sorted.mean()) * 100
            st.metric(
                "Diferença Média",
                f"{diff:.0f} bytes",
                delta=f"{reduction_pct:.1f}% de redução"
            )
        
        with col2:
            ci_lower = test_results['ci_lower']
            ci_upper = test_results['ci_upper']
            st.metric(
                "IC 95%",
                f"[{ci_lower:.0f}, {ci_upper:.0f}] bytes"
            )
        
        with col3:
            d = test_results['cohens_d']
            st.metric(
                "Tamanho do Efeito (Cohen's d)",
                f"{d:.3f}",
                delta=test_results['d_interpretation']
            )
        
        st.markdown("---")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Histograma Comparativo")
            fig_hist = create_histogram_comparison(df, 'size_bytes', 'Tamanho da Resposta (bytes)')
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            st.subheader("📊 Gráfico de Barras")
            fig_bar = create_bar_comparison(df, 'size_bytes', 'Tamanho da Resposta (bytes)')
            st.plotly_chart(fig_bar, use_container_width=True)
        
        st.subheader("🔍 Comparação REST vs GraphQL por ID")
        fig_scatter = create_scatter_comparison(df, 'size_bytes', 'Tamanho (bytes)')
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Resultados dos testes estatísticos
        st.markdown("---")
        st.subheader("🔬 Resultados dos Testes Estatísticos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Teste de Normalidade (Shapiro-Wilk)")
            st.write(f"**Estatística:** {test_results['shapiro_stat']:.4f}")
            st.write(f"**p-valor:** {test_results['shapiro_p']:.4f}")
            if test_results['is_normal']:
                st.success("✅ Dados seguem distribuição normal (p > 0.05)")
            else:
                st.warning("⚠️ Dados não seguem distribuição normal (p ≤ 0.05)")
        
        with col2:
            st.markdown(f"##### {test_results['test_name']}")
            st.write(f"**Estatística:** {test_results['test_stat']:.4f}")
            st.write(f"**p-valor:** {test_results['test_p']:.4f}")
            
            alpha = 0.05
            if test_results['test_p'] < alpha:
                st.success(f"✅ Diferença estatisticamente significativa (p < {alpha})")
                if diff > 0:
                    st.info("📊 GraphQL retorna respostas **significativamente menores** que REST")
                else:
                    st.info("📊 REST retorna respostas **significativamente menores** que GraphQL")
            else:
                st.warning(f"⚠️ Diferença não estatisticamente significativa (p ≥ {alpha})")
        
        # Interpretação
        st.markdown("---")
        st.subheader("💡 Interpretação dos Resultados")
        
        interpretation = f"""
        **Hipótese Nula (H₀):** μ_GraphQL ≥ μ_REST  
        **Hipótese Alternativa (H₁):** μ_GraphQL < μ_REST
        
        - **Diferença média:** {diff:.0f} bytes (REST - GraphQL)
        - **Redução percentual:** {reduction_pct:.1f}%
        - **Teste utilizado:** {test_results['test_name']}
        - **Tamanho do efeito:** {d:.3f} ({test_results['d_interpretation']})
        - **Intervalo de confiança 95%:** [{ci_lower:.0f}, {ci_upper:.0f}] bytes
        
        """
        
        if test_results['test_p'] < 0.05:
            if diff > 0:
                interpretation += "**Conclusão:** Rejeitamos H₀. GraphQL retorna respostas **significativamente menores** que REST."
            else:
                interpretation += "**Conclusão:** Rejeitamos H₀. REST retorna respostas **significativamente menores** que GraphQL."
        else:
            interpretation += "**Conclusão:** Não rejeitamos H₀. Não há evidência suficiente de diferença significativa entre os tamanhos das respostas."
        
        st.markdown(interpretation)
    
    # PÁGINA 4: ANÁLISE DETALHADA
    elif page == "Análise Detalhada":
        st.title("🔍 Análise Detalhada")
        st.markdown("---")
        
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            min_id = int(df['id'].min())
            max_id = int(df['id'].max())
            id_range = st.slider(
                "Filtrar por ID",
                min_value=min_id,
                max_value=max_id,
                value=(min_id, max_id)
            )
        
        with col2:
            api_filter = st.multiselect(
                "Filtrar por Tipo de API",
                options=['REST', 'GraphQL'],
                default=['REST', 'GraphQL']
            )
        
        # Aplicar filtros
        filtered_df = df[
            (df['id'] >= id_range[0]) & 
            (df['id'] <= id_range[1]) &
            (df['type'].isin(api_filter))
        ].copy()
        
        st.markdown("---")
        
        # Tabela interativa
        st.subheader("📋 Dados Filtrados")
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Estatísticas dos dados filtrados
        st.markdown("---")
        st.subheader("📊 Estatísticas dos Dados Filtrados")
        
        if len(api_filter) > 0:
            col1, col2 = st.columns(2)
            
            for idx, api_type in enumerate(api_filter):
                with col1 if idx == 0 else col2:
                    st.markdown(f"##### {api_type}")
                    filtered_type = filtered_df[filtered_df['type'] == api_type]
                    
                    if len(filtered_type) > 0:
                        st.write(f"**Tempo de Resposta:**")
                        st.write(f"- Média: {filtered_type['time_ms'].mean():.2f} ms")
                        st.write(f"- Mediana: {filtered_type['time_ms'].median():.2f} ms")
                        st.write(f"- DP: {filtered_type['time_ms'].std():.2f} ms")
                        
                        st.write(f"**Tamanho da Resposta:**")
                        st.write(f"- Média: {filtered_type['size_bytes'].mean():.0f} bytes")
                        st.write(f"- Mediana: {filtered_type['size_bytes'].median():.0f} bytes")
                        st.write(f"- DP: {filtered_type['size_bytes'].std():.0f} bytes")
        
        # Gráfico de correlação
        st.markdown("---")
        st.subheader("🔗 Correlação entre Tempo e Tamanho")
        
        fig_corr = px.scatter(
            filtered_df,
            x='time_ms',
            y='size_bytes',
            color='type',
            color_discrete_map=COLORS,
            size='id',
            hover_data=['id'],
            title='Correlação entre Tempo de Resposta e Tamanho da Resposta',
            labels={'time_ms': 'Tempo de Resposta (ms)', 'size_bytes': 'Tamanho da Resposta (bytes)'}
        )
        fig_corr.update_layout(height=500, template='plotly_white')
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Calcular correlação
        if len(filtered_df) > 1:
            corr_rest = filtered_df[filtered_df['type'] == 'REST'][['time_ms', 'size_bytes']].corr().iloc[0, 1]
            corr_graphql = filtered_df[filtered_df['type'] == 'GraphQL'][['time_ms', 'size_bytes']].corr().iloc[0, 1]
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Correlação REST", f"{corr_rest:.3f}")
            with col2:
                st.metric("Correlação GraphQL", f"{corr_graphql:.3f}")
        
        # Exportação
        st.markdown("---")
        st.subheader("💾 Exportação de Dados")
        
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Dados Filtrados (CSV)",
            data=csv,
            file_name=f"filtered_data_{id_range[0]}_{id_range[1]}.csv",
            mime="text/csv"
        )

else:
    st.error("Erro ao carregar os dados. Verifique se o arquivo experiment_results.csv existe.")

