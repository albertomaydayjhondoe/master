#!/usr/bin/env python3
"""
Dashboard Streamlit para Estadísticas de Modelos COCO y YOLO
Análisis detallado de rendimiento, precisión y métricas de modelos ML
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
import time
from datetime import datetime, timedelta
from PIL import Image
import io
import base64
from typing import Dict, List, Any, Optional
import sqlite3
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="🎯 COCO/YOLO Analytics",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de la API
API_BASE = "http://localhost:8000"
API_V1 = f"{API_BASE}/api/v1"
API_KEY = "dummy_development_key"
HEADERS = {"X-API-Key": API_KEY}

class ModelAnalytics:
    """Clase para análisis de modelos."""
    
    def __init__(self):
        self.db_path = "data/model_analytics.db"
        Path(self.db_path).parent.mkdir(exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Inicializar base de datos de analytics."""
        with sqlite3.connect(self.db_path) as conn:
            # Tabla para detecciones
            conn.execute("""
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    model_name TEXT NOT NULL,
                    image_name TEXT,
                    total_detections INTEGER,
                    social_relevant_count INTEGER,
                    processing_time_ms REAL,
                    confidence_avg REAL,
                    confidence_max REAL,
                    confidence_min REAL,
                    classes_detected TEXT,
                    image_size TEXT,
                    detection_data TEXT
                )
            """)
            
            # Tabla para métricas por clase
            conn.execute("""
                CREATE TABLE IF NOT EXISTS class_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    model_name TEXT NOT NULL,
                    class_name TEXT NOT NULL,
                    detections_count INTEGER,
                    confidence_avg REAL,
                    confidence_std REAL,
                    bbox_area_avg REAL,
                    social_relevant BOOLEAN
                )
            """)
            
            # Tabla para benchmarks de modelos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_benchmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    model_name TEXT NOT NULL,
                    test_images_count INTEGER,
                    avg_processing_time REAL,
                    total_detections INTEGER,
                    precision_score REAL,
                    recall_score REAL,
                    f1_score REAL,
                    map_score REAL,
                    benchmark_data TEXT
                )
            """)
    
    def log_detection(self, detection_data: Dict[str, Any], model_name: str, image_name: str = None):
        """Registrar detección en la base de datos."""
        detections = detection_data.get('detections', [])
        
        if not detections:
            return
        
        # Calcular estadísticas
        confidences = [d['confidence'] for d in detections]
        social_count = sum(1 for d in detections if d.get('social_relevant', False))
        classes = list(set(d['class_name'] for d in detections))
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO detections (
                    model_name, image_name, total_detections, social_relevant_count,
                    processing_time_ms, confidence_avg, confidence_max, confidence_min,
                    classes_detected, detection_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                model_name,
                image_name,
                len(detections),
                social_count,
                detection_data.get('processing_time_ms', 0),
                np.mean(confidences),
                max(confidences),
                min(confidences),
                json.dumps(classes),
                json.dumps(detection_data)
            ))
    
    def get_model_stats(self, hours: int = 24) -> pd.DataFrame:
        """Obtener estadísticas de modelos."""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT * FROM detections 
                WHERE timestamp > datetime('now', '-{} hours')
                ORDER BY timestamp DESC
            """.format(hours)
            return pd.read_sql_query(query, conn)
    
    def get_class_performance(self, model_name: str = None, hours: int = 24) -> pd.DataFrame:
        """Obtener rendimiento por clase."""
        with sqlite3.connect(self.db_path) as conn:
            where_clause = "WHERE timestamp > datetime('now', '-{} hours')".format(hours)
            if model_name:
                where_clause += f" AND model_name = '{model_name}'"
            
            query = f"SELECT * FROM class_metrics {where_clause} ORDER BY timestamp DESC"
            return pd.read_sql_query(query, conn)

# Instancia global
analytics = ModelAnalytics()

def create_test_image() -> bytes:
    """Crear imagen de prueba."""
    image = Image.new('RGB', (640, 480), color='lightblue')
    from PIL import ImageDraw
    draw = ImageDraw.Draw(image)
    
    # Agregar formas
    draw.rectangle([100, 100, 200, 200], fill='red')
    draw.rectangle([300, 200, 400, 350], fill='blue')
    draw.ellipse([450, 50, 550, 150], fill='green')
    
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='JPEG')
    return img_bytes.getvalue()

def test_model_api(model_name: str, confidence: float) -> Dict[str, Any]:
    """Probar API del modelo."""
    try:
        image_bytes = create_test_image()
        
        files = {'file': ('test.jpg', image_bytes, 'image/jpeg')}
        params = {
            'model_name': model_name,
            'conf_threshold': confidence,
            'social_only': False
        }
        
        start_time = time.time()
        response = requests.post(
            f"{API_V1}/coco_detect",
            headers=HEADERS,
            files=files,
            params=params,
            timeout=30
        )
        request_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            data['request_time_ms'] = request_time
            
            # Registrar en analytics
            analytics.log_detection(data, model_name, "test_image")
            
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_available_models() -> List[str]:
    """Obtener modelos disponibles."""
    try:
        response = requests.get(f"{API_V1}/coco_models", headers=HEADERS, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('available_models', ['yolov8n.pt'])
        return ['yolov8n.pt']
    except:
        return ['yolov8n.pt']

def get_coco_classes() -> Dict[str, Any]:
    """Obtener clases COCO."""
    try:
        response = requests.get(f"{API_V1}/coco_classes", headers=HEADERS, timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"classes": [], "social_relevant": []}
    except:
        return {"classes": [], "social_relevant": []}

def create_performance_chart(df: pd.DataFrame) -> go.Figure:
    """Crear gráfico de rendimiento."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No hay datos disponibles", 
                          xref="paper", yref="paper", 
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Detecciones por Modelo', 'Tiempo de Procesamiento', 
                       'Confianza Promedio', 'Objetos Sociales'),
        specs=[[{'type': 'bar'}, {'type': 'scatter'}],
               [{'type': 'box'}, {'type': 'pie'}]]
    )
    
    # Detecciones por modelo
    model_counts = df.groupby('model_name')['total_detections'].sum()
    fig.add_trace(
        go.Bar(x=model_counts.index, y=model_counts.values, name='Detecciones'),
        row=1, col=1
    )
    
    # Tiempo de procesamiento
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['processing_time_ms'], 
                  mode='lines+markers', name='Tiempo (ms)'),
        row=1, col=2
    )
    
    # Box plot de confianza
    for model in df['model_name'].unique():
        model_data = df[df['model_name'] == model]
        fig.add_trace(
            go.Box(y=model_data['confidence_avg'], name=model),
            row=2, col=1
        )
    
    # Pie chart de objetos sociales
    social_total = df['social_relevant_count'].sum()
    non_social_total = df['total_detections'].sum() - social_total
    
    fig.add_trace(
        go.Pie(labels=['Sociales', 'No Sociales'], 
               values=[social_total, non_social_total],
               name="Relevancia Social"),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=True, title_text="Métricas de Rendimiento")
    return fig

def main():
    """Función principal del dashboard."""
    st.title("🎯 TikTok Viral ML - Análisis de Modelos COCO/YOLO")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Selección de modelo
        available_models = get_available_models()
        selected_model = st.selectbox("Modelo YOLO", available_models)
        
        # Configuración de confianza
        confidence_threshold = st.slider("Umbral de Confianza", 0.1, 1.0, 0.25, 0.05)
        
        # Rango de tiempo
        time_range = st.selectbox(
            "Rango de Tiempo",
            [("1 hora", 1), ("6 horas", 6), ("24 horas", 24), ("7 días", 168)],
            index=2,
            format_func=lambda x: x[0]
        )[1]
        
        st.divider()
        
        # Test del modelo
        st.header("🧪 Test de Modelo")
        if st.button("▶️ Probar Modelo", type="primary"):
            with st.spinner("Probando modelo..."):
                result = test_model_api(selected_model, confidence_threshold)
                
                if result["success"]:
                    st.success("✅ Test exitoso!")
                    data = result["data"]
                    st.metric("Detecciones", data["total_detections"])
                    st.metric("Tiempo", f"{data['request_time_ms']:.1f} ms")
                    st.metric("Sociales", data["social_relevant_count"])
                else:
                    st.error(f"❌ Error: {result['error']}")
    
    # Contenido principal
    col1, col2, col3, col4 = st.columns(4)
    
    # Métricas rápidas
    df_stats = analytics.get_model_stats(time_range)
    
    with col1:
        total_tests = len(df_stats)
        st.metric("Tests Ejecutados", total_tests)
    
    with col2:
        if not df_stats.empty:
            avg_time = df_stats['processing_time_ms'].mean()
            st.metric("Tiempo Promedio", f"{avg_time:.1f} ms")
        else:
            st.metric("Tiempo Promedio", "N/A")
    
    with col3:
        if not df_stats.empty:
            total_detections = df_stats['total_detections'].sum()
            st.metric("Total Detecciones", total_detections)
        else:
            st.metric("Total Detecciones", 0)
    
    with col4:
        if not df_stats.empty:
            avg_confidence = df_stats['confidence_avg'].mean()
            st.metric("Confianza Promedio", f"{avg_confidence:.3f}")
        else:
            st.metric("Confianza Promedio", "N/A")
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Análisis General", "🎯 Por Clases", "🔄 Comparación", "📈 Benchmark"])
    
    with tab1:
        st.header("📊 Análisis General de Rendimiento")
        
        if not df_stats.empty:
            # Gráfico principal
            fig = create_performance_chart(df_stats)
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla de datos recientes
            st.subheader("📋 Detecciones Recientes")
            display_df = df_stats[['timestamp', 'model_name', 'total_detections', 
                                 'social_relevant_count', 'processing_time_ms', 'confidence_avg']].head(10)
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No hay datos disponibles. Ejecuta algunos tests para ver estadísticas.")
    
    with tab2:
        st.header("🎯 Análisis por Clases COCO")
        
        # Obtener información de clases
        coco_info = get_coco_classes()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Clases Disponibles")
            if coco_info.get("classes"):
                classes_df = pd.DataFrame({
                    "Clase": coco_info["classes"][:20],  # Mostrar primeras 20
                    "ID": range(len(coco_info["classes"][:20]))
                })
                st.dataframe(classes_df, use_container_width=True)
            else:
                st.info("No se pudieron cargar las clases COCO")
        
        with col2:
            st.subheader("🎯 Clases Socialmente Relevantes")
            if coco_info.get("social_relevant"):
                social_df = pd.DataFrame({
                    "Clase Social": coco_info["social_relevant"]
                })
                st.dataframe(social_df, use_container_width=True)
            else:
                st.info("No hay clases sociales definidas")
        
        # Análisis de detecciones por clase
        if not df_stats.empty:
            st.subheader("📊 Frecuencia de Detección por Clase")
            
            # Procesar datos de clases detectadas
            all_classes = []
            for _, row in df_stats.iterrows():
                try:
                    classes = json.loads(row['classes_detected'])
                    all_classes.extend(classes)
                except:
                    continue
            
            if all_classes:
                class_counts = pd.Series(all_classes).value_counts()
                
                fig_classes = px.bar(
                    x=class_counts.index[:15], 
                    y=class_counts.values[:15],
                    title="Top 15 Clases Más Detectadas"
                )
                st.plotly_chart(fig_classes, use_container_width=True)
    
    with tab3:
        st.header("🔄 Comparación de Modelos")
        
        if not df_stats.empty:
            # Comparación de modelos
            model_comparison = df_stats.groupby('model_name').agg({
                'total_detections': ['count', 'mean', 'sum'],
                'processing_time_ms': ['mean', 'std'],
                'confidence_avg': ['mean', 'std'],
                'social_relevant_count': ['mean', 'sum']
            }).round(3)
            
            model_comparison.columns = ['Tests', 'Detecciones/Test', 'Total Detecciones',
                                      'Tiempo Medio', 'Tiempo StdDev', 'Confianza Media', 
                                      'Confianza StdDev', 'Sociales/Test', 'Total Sociales']
            
            st.subheader("📊 Tabla Comparativa")
            st.dataframe(model_comparison, use_container_width=True)
            
            # Gráfico de comparación
            fig_comparison = go.Figure()
            
            for model in df_stats['model_name'].unique():
                model_data = df_stats[df_stats['model_name'] == model]
                fig_comparison.add_trace(
                    go.Scatter(
                        x=model_data['processing_time_ms'],
                        y=model_data['confidence_avg'],
                        mode='markers',
                        name=model,
                        text=model_data['total_detections'],
                        hovertemplate='<b>%{fullData.name}</b><br>' +
                                    'Tiempo: %{x:.1f} ms<br>' +
                                    'Confianza: %{y:.3f}<br>' +
                                    'Detecciones: %{text}<extra></extra>'
                    )
                )
            
            fig_comparison.update_layout(
                title="Rendimiento vs Precisión por Modelo",
                xaxis_title="Tiempo de Procesamiento (ms)",
                yaxis_title="Confianza Promedio"
            )
            
            st.plotly_chart(fig_comparison, use_container_width=True)
    
    with tab4:
        st.header("📈 Benchmark y Métricas Avanzadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚀 Ejecutar Benchmark")
            
            benchmark_images = st.number_input("Número de imágenes de test", 1, 100, 10)
            benchmark_model = st.selectbox("Modelo para benchmark", available_models, key="benchmark")
            
            if st.button("▶️ Ejecutar Benchmark"):
                progress_bar = st.progress(0)
                results = []
                
                for i in range(benchmark_images):
                    result = test_model_api(benchmark_model, confidence_threshold)
                    if result["success"]:
                        results.append(result["data"])
                    progress_bar.progress((i + 1) / benchmark_images)
                
                if results:
                    # Calcular métricas del benchmark
                    total_detections = sum(r["total_detections"] for r in results)
                    avg_time = np.mean([r["processing_time_ms"] for r in results])
                    avg_confidence = np.mean([r.get("confidence_avg", 0) for r in results])
                    
                    st.success(f"✅ Benchmark completado!")
                    st.metric("Detecciones totales", total_detections)
                    st.metric("Tiempo promedio", f"{avg_time:.1f} ms")
                    st.metric("Confianza promedio", f"{avg_confidence:.3f}")
        
        with col2:
            st.subheader("📊 Métricas Históricas")
            
            if not df_stats.empty:
                # Tendencias temporales
                df_time = df_stats.copy()
                df_time['timestamp'] = pd.to_datetime(df_time['timestamp'])
                df_time = df_time.set_index('timestamp').resample('1H').agg({
                    'total_detections': 'sum',
                    'processing_time_ms': 'mean',
                    'confidence_avg': 'mean'
                }).dropna()
                
                if not df_time.empty:
                    fig_trends = make_subplots(rows=3, cols=1, 
                                             subplot_titles=('Detecciones/Hora', 'Tiempo Medio', 'Confianza Media'))
                    
                    fig_trends.add_trace(
                        go.Scatter(x=df_time.index, y=df_time['total_detections'], name='Detecciones'),
                        row=1, col=1
                    )
                    
                    fig_trends.add_trace(
                        go.Scatter(x=df_time.index, y=df_time['processing_time_ms'], name='Tiempo (ms)'),
                        row=2, col=1
                    )
                    
                    fig_trends.add_trace(
                        go.Scatter(x=df_time.index, y=df_time['confidence_avg'], name='Confianza'),
                        row=3, col=1
                    )
                    
                    fig_trends.update_layout(height=600, title_text="Tendencias Temporales")
                    st.plotly_chart(fig_trends, use_container_width=True)
            else:
                st.info("No hay suficientes datos para mostrar tendencias")
    
    # Footer
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("🔗 **API ML**: http://localhost:8000")
    
    with col2:
        st.info("🎯 **Gradio Manager**: http://localhost:7860")
    
    with col3:
        if st.button("🔄 Refrescar Datos"):
            st.rerun()

if __name__ == "__main__":
    main()