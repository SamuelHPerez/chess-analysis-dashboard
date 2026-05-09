# ♟️ Chess Intelligence Hub
### *Dashboard de Análisis Estadístico y Táctico*

---

## 🇪🇸 Español

Este repositorio contiene una aplicación interactiva diseñada para centralizar y analizar partidas de ajedrez. La herramienta permite visualizar el rendimiento histórico y realizar análisis profundos de jugadas utilizando motores de evaluación en tiempo real.

### 🛠️ Tecnologías Utilizadas
* **Streamlit**: Interfaz de usuario y diseño *Dark Mode*.
* **Python-Chess**: Gestión de estados del tablero y procesamiento de archivos PGN.
* **Plotly**: Generación de gráficos de progresión y distribución de resultados.
* **Stockfish API**: Integración de evaluaciones de motor para análisis táctico.
* **Pandas**: Procesamiento de datos provenientes de la API de Chess.com.

### 🚀 Funcionalidades
* **📈 Dashboard de Rendimiento**: Visualización de la evolución del rating y estadísticas de efectividad por día y color de piezas.
* **🔄 Selector de Perspectiva**: Control global para cambiar la orientación del tablero y filtrar estadísticas según el bando (White/Black).
* **⚙️ Análisis con Motor**: Barra de ventaja dinámica y sugerencia de mejores jugadas basadas en la posición actual.
* **🖼️ Visor de Partidas**: Navegación paso a paso de archivos PGN o historiales descargados directamente de la cuenta de usuario.
* **🧪 Playground**: Entorno libre para pruebas de variantes y entrenamiento táctico.

### ⚙️ Configuración e Instalación
1.  **Clonar el repositorio**:
    ```bash
    git clone [https://github.com/SamuelHPerez/chess-analysis-dashboard.git](https://github.com/SamuelHPerez/chess-analysis-dashboard.git)
    ```
2.  **Instalar las dependencias**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Iniciar la aplicación**:
    ```bash
    streamlit run app.py
    ```

---

## 🇺🇸 English

This repository features an interactive application designed to centralize and analyze chess games. The tool enables users to visualize historical performance and perform deep-dive move analysis using real-time evaluation engines.

### 🛠️ Tech Stack
* **Streamlit**: UI development and Dark Mode implementation.
* **Python-Chess**: Board state management and PGN file processing.
* **Plotly**: Interactive rating progression and result distribution charts.
* **Stockfish API**: Engine evaluation integration for tactical analysis.
* **Pandas**: Data processing for records retrieved from the Chess.com API.

### 🚀 Key Features
* **📈 Performance Dashboard**: Visualization of rating progression and win-rate statistics by day and piece color.
* **🔄 Perspective Selector**: Global control to toggle board orientation and filter statistics based on side (White/Black).
* **⚙️ Engine Analysis**: Dynamic advantage bar and best-move suggestions based on the current position.
* **🖼️ Game Viewer**: Step-by-step navigation for PGN files or match histories downloaded directly from user accounts.
* **🧪 Playground**: A tactical sandbox for move testing and variant training.

### ⚙️ Setup & Installation
1.  **Clone the repository**:
    ```bash
    git clone [https://github.com/SamuelHPerez/chess-analysis-dashboard.git](https://github.com/SamuelHPerez/chess-analysis-dashboard.git)
    ```
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the application**:
    ```bash
    streamlit run app.py
    ```

---

**🔗 Links:**
* **Live App:** [https://chessanalysis.streamlit.app](https://chessanalysis.streamlit.app)