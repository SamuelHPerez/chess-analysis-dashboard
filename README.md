# Chess Intelligence Hub
### *Dashboard de Análisis Estadístico y Táctico*

Este repositorio contiene una aplicación interactiva diseñada para centralizar y analizar partidas de ajedrez. La herramienta permite visualizar el rendimiento histórico y realizar análisis profundos de jugadas utilizando motores de evaluación en tiempo real.

## Tecnologías Utilizadas
* **Streamlit**: Interfaz de usuario y diseño Dark Mode.
* **Python-Chess**: Gestión de estados del tablero y procesamiento de archivos PGN.
* **Plotly**: Generación de gráficos de progresión y distribución de resultados.
* **Stockfish API**: Integración de evaluaciones de motor para análisis táctico.
* **Pandas**: Procesamiento de datos provenientes de la API de Chess.com.

## Funcionalidades
* **Dashboard de Rendimiento**: Visualización de la evolución del rating y estadísticas de efectividad por día y color de piezas.
* **Selector de Perspectiva**: Control global para cambiar la orientación del tablero y filtrar estadísticas según el bando (Blanco/Negro).
* **Análisis con Motor**: Barra de ventaja dinámica y sugerencia de mejores jugadas basadas en la posición actual.
* **Visor de Partidas**: Navegación paso a paso de archivos PGN o historiales descargados directamente de la cuenta de usuario.
* **Playground**: Entorno libre para pruebas de variantes y entrenamiento táctico.

## ⚙Configuración e Instalación
1.  Clonar el repositorio:
    ```bash
    git clone [https://github.com/Samuel/Chess-Intelligence-Hub.git](https://github.com/Samuel/Chess-Intelligence-Hub.git)
    ```
2.  Instalar las dependencias necesarias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Iniciar la aplicación localmente:
    ```bash
    streamlit run app.py