# 🏥 Telegram Medical Data Pipeline

**Complete End-to-End Data Pipeline for Ethiopian Medical Business Analytics**

A production-ready data pipeline that extracts, transforms, and analyzes medical business data from Telegram channels using modern data engineering tools.

## 🎯 Project Status: **ALL TASKS COMPLETE** ✅

| Task | Status | Description |
|------|--------|-------------|
| **Task 1** | ✅ **COMPLETE** | Data Scraping and Collection (Telegram) |
| **Task 2** | ✅ **COMPLETE** | Data Modeling and Transformation (dbt) |
| **Task 3** | ✅ **COMPLETE** | Data Enrichment with Object Detection (YOLO) |
| **Task 4** | ✅ **COMPLETE** | Analytical API Development (FastAPI) |
| **Task 5** | ✅ **COMPLETE** | Pipeline Orchestration (Dagster) |

## 🏗️ Architecture Overview

This project implements a complete **ELT (Extract, Load, Transform)** pipeline for analyzing medical business data from Ethiopian Telegram channels:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram      │    │   PostgreSQL    │    │   dbt           │    │   FastAPI       │
│   Channels      │───▶│   Data          │───▶│   Transformations│───▶│   Analytics     │
│   (19 channels) │    │   Warehouse     │    │   (Star Schema) │    │   API           │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   YOLOv8        │    │   Dagster       │    │   Data Quality  │    │   Real-time     │
│   Object        │    │   Orchestration │    │   Monitoring    │    │   Insights      │
│   Detection     │    │   & Scheduling  │    │   & Testing     │    │   & Analytics   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Key Features

### 📊 **Data Pipeline**
- **Automated Telegram Scraping**: 19 Ethiopian medical channels
- **Real-time Data Processing**: Continuous data ingestion
- **Data Lake Architecture**: Raw data storage with partitioning
- **Star Schema Modeling**: Optimized for analytics
- **Data Quality Assurance**: Comprehensive testing and validation

### 🤖 **AI-Powered Analysis**
- **YOLOv8 Object Detection**: Medical product identification
- **Image Content Analysis**: Automated image processing
- **Medical Keyword Detection**: Intelligent text analysis
- **Price Pattern Recognition**: Automated price extraction

### 🔧 **Production Infrastructure**
- **Dagster Orchestration**: Complete pipeline automation
- **Scheduled Execution**: Automated data processing
- **Error Handling**: Robust error recovery
- **Monitoring**: Real-time pipeline health
- **Scalability**: Containerized architecture

### 📈 **Analytics & API**
- **RESTful API**: FastAPI-based analytics endpoints
- **Real-time Insights**: Live data analytics
- **Business Intelligence**: Pre-built analytical queries
- **Data Visualization**: Ready for dashboard integration

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Data Extraction** | Telethon (Telegram API) | Channel scraping |
| **Data Storage** | PostgreSQL | Data warehouse |
| **Data Transformation** | dbt (data build tool) | ETL/ELT processing |
| **Data Enrichment** | YOLOv8 (Ultralytics) | Object detection |
| **Orchestration** | Dagster | Pipeline management |
| **API Framework** | FastAPI | Analytics API |
| **Containerization** | Docker & Docker Compose | Deployment |
| **Language** | Python 3.11+ | Backend development |

## 📁 Project Structure

```
telegram-medical-data-pipeline/
├── 📂 app/                          # FastAPI Application
│   ├── 📂 api/                     # API endpoints & schemas
│   │   ├── 📂 routes/              # API route definitions
│   │   ├── database.py             # Database connection
│   │   ├── crud.py                 # Data access layer
│   │   ├── schemas.py              # Pydantic models
│   │   └── main.py                 # FastAPI app
│   ├── 📂 core/                    # Core configuration
│   │   ├── config.py               # App settings
│   │   ├── channels_config.py      # Telegram channels
│   │   └── logging_config.py       # Logging setup
│   └── 📂 services/                # Business logic
│       ├── telegram_scraper.py     # Telegram scraping
│       ├── data_loader.py          # Data loading
│       └── yolo_detector.py        # YOLO detection
├── 📂 dagster_workspace/           # Dagster Orchestration
│   ├── 📂 assets/                  # Data assets
│   │   ├── telegram_assets.py      # Telegram pipeline
│   │   ├── dbt_assets.py           # dbt transformations
│   │   └── yolo_assets.py          # YOLO processing
│   ├── 📂 jobs/                    # Pipeline jobs
│   ├── 📂 schedules/               # Automated schedules
│   ├── 📂 sensors/                 # Event triggers
│   └── workspace.py                # Dagster config
├── 📂 dbt/                         # dbt Transformations
│   └── telegram_medical_pipeline/  # dbt project
│       ├── 📂 models/              # Data models
│       │   ├── 📂 staging/         # Staging models
│       │   └── 📂 marts/           # Mart models
│       ├── 📂 tests/               # Data tests
│       └── dbt_project.yml         # dbt config
├── 📂 data/                        # Data Storage
│   ├── 📂 raw/                     # Raw data lake
│   ├── 📂 processed/               # Processed data
│   └── 📂 enriched/                # YOLO results
├── 📂 scripts/                     # Utility Scripts
│   ├── run_scraper.py              # Telegram scraper
│   ├── run_dbt.py                  # dbt runner
│   ├── run_yolo_pipeline.py        # YOLO pipeline
│   ├── run_api.py                  # FastAPI server
│   └── run_dagster.py              # Dagster UI
├── 📂 logs/                        # Application logs
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Application container
├── docker-compose.yml              # Service orchestration
├── init.sql                        # Database schema
└── README.md                       # Project documentation
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose**
- **PostgreSQL** (or use Docker)
- **Telegram API credentials**

### 1. Clone & Setup

```bash
# Clone repository
git clone https://github.com/BruhTes/telegram-medical-data-pipeline.git
cd telegram-medical-data-pipeline

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required Environment Variables:**
```env
# Telegram API (Required)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+251912345678

# Database (Required)
POSTGRES_DB=telegram_medical
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Application (Optional)
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

### 3. Start Services

```bash
# Option A: Using Docker (Recommended)
docker-compose up -d

# Option B: Local PostgreSQL + Python
# Start PostgreSQL separately, then:
python scripts/setup_database.py
```

### 4. Access Services

| Service | URL | Description |
|---------|-----|-------------|
| **FastAPI Analytics** | http://localhost:8000 | Main analytics API |
| **Dagster UI** | http://localhost:3000 | Pipeline orchestration |
| **dbt Docs** | http://localhost:8080 | Data documentation |
| **PostgreSQL** | localhost:5432 | Database |

## 📊 Pipeline Components

### 🔍 **Task 1: Data Scraping & Collection**
- **19 Ethiopian Medical Channels** configured
- **Automated scraping** every 4 hours
- **Media download** for image analysis
- **Data lake storage** with partitioning
- **Comprehensive logging** and error handling

### 🔄 **Task 2: Data Modeling & Transformation**
- **dbt star schema** implementation
- **5 data models**: staging + marts
- **Data quality tests** and validation
- **Automated documentation** generation
- **Incremental processing** support

### 🤖 **Task 3: YOLO Object Detection**
- **YOLOv8 integration** for image analysis
- **Medical object detection** (pills, bottles, etc.)
- **Confidence scoring** and filtering
- **Batch processing** capabilities
- **Detection metadata** storage

### 🌐 **Task 4: FastAPI Analytics API**
- **12 RESTful endpoints** for analytics
- **Real-time data access** to dbt models
- **Pydantic validation** and documentation
- **Pagination** and filtering support
- **Comprehensive error handling**

### ⚙️ **Task 5: Dagster Orchestration**
- **4 pipeline jobs** for different stages
- **5 automated schedules** for execution
- **4 event-driven sensors** for triggers
- **Asset lineage** and monitoring
- **Production-ready** orchestration

## 📈 API Endpoints

### 🔍 **Analytics Endpoints**
```http
GET /api/analytics/summary                    # Overall pipeline summary
GET /api/channels                             # List all channels
GET /api/channels/{channel}/activity          # Channel activity
GET /api/search/messages?query=paracetamol    # Message search
GET /api/reports/top-products?limit=10        # Top products
GET /api/reports/channel-rankings             # Channel rankings
GET /api/image-detections                     # YOLO detection results
GET /api/reports/medical-insights             # Medical insights
```

### 📊 **Data Endpoints**
```http
GET /health                                   # Health check
GET /docs                                     # API documentation
GET /redoc                                    # Alternative docs
```

## 🔧 Development Commands

### Pipeline Management
```bash
# Run Telegram scraper
python scripts/run_scraper.py

# Run dbt transformations
python scripts/run_dbt.py full-pipeline

# Run YOLO detection
python scripts/run_yolo_pipeline.py

# Start FastAPI server
python scripts/run_api.py

# Start Dagster UI
python scripts/run_dagster.py dev
```

### Dagster Commands
```bash
# List available jobs
python scripts/run_dagster.py list-jobs

# List schedules
python scripts/run_dagster.py list-schedules

# Run specific job
python scripts/run_dagster.py run --job telegram_pipeline_job
```

### dbt Commands
```bash
# Run all models
python scripts/run_dbt.py run

# Run tests
python scripts/run_dbt.py test

# Generate docs
python scripts/run_dbt.py docs-generate

# Serve docs
python scripts/run_dbt.py docs-serve
```

## 📊 Data Models

### Star Schema Structure
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   dim_channels  │    │   fct_messages  │    │   dim_dates     │
│                 │◄───┤                 ├────►│                 │
│ • channel_id    │    │ • message_id    │    │ • date_id       │
│ • channel_name  │    │ • channel_id    │    │ • date          │
│ • category      │    │ • date_id       │    │ • day_of_week   │
│ • priority      │    │ • message_text  │    │ • month         │
│ • activity_level│    │ • has_media     │    │ • quarter       │
└─────────────────┘    │ • message_type  │    └─────────────────┘
                       │ • content_type  │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │fct_image_detections│
                       │                 │
                       │ • detection_id  │
                       │ • message_id    │
                       │ • object_class  │
                       │ • confidence    │
                       │ • is_medical    │
                       └─────────────────┘
```

## 🔄 Automation & Scheduling

### Dagster Schedules
| Schedule | Frequency | Job | Purpose |
|----------|-----------|-----|---------|
| `daily_pipeline_schedule` | Daily 6:00 AM | `full_pipeline_job` | Complete pipeline |
| `telegram_data_schedule` | Every 4 hours | `telegram_pipeline_job` | Data collection |
| `dbt_transformation_schedule` | Every 6 hours | `dbt_job` | Data transformation |
| `yolo_detection_schedule` | Every 12 hours | `yolo_job` | Image analysis |
| `weekly_refresh_schedule` | Sunday 2:00 AM | `full_pipeline_job` | Full refresh |

### Event-Driven Triggers
- **Time-based sensors** for automated execution
- **Data availability** triggers
- **Quality gate** validation
- **Error recovery** mechanisms

## 🧪 Testing & Quality

### Data Quality Tests
- **dbt built-in tests**: `unique`, `not_null`
- **Custom data tests**: Business rule validation
- **Data completeness** checks
- **Data freshness** monitoring

### Pipeline Monitoring
- **Asset lineage** tracking
- **Execution history** logging
- **Performance metrics** collection
- **Error rate** monitoring

## 🚀 Production Deployment

### Docker Deployment
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale app=3
```

### Environment Configuration
- **Production** environment variables
- **Database** connection pooling
- **Logging** configuration
- **Security** settings

## 📈 Performance & Scalability

### Current Capabilities
- **19 Telegram channels** monitored
- **Real-time processing** pipeline
- **Automated scheduling** system
- **Scalable architecture** design

### Optimization Features
- **Incremental processing** for efficiency
- **Parallel execution** where possible
- **Resource optimization** for cost
- **Caching strategies** for performance

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Add** tests and documentation
5. **Submit** a pull request

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Issues

- **GitHub Issues**: [Report bugs](https://github.com/BruhTes/telegram-medical-data-pipeline/issues)
- **Documentation**: [Wiki](https://github.com/BruhTes/telegram-medical-data-pipeline/wiki)
- **Discussions**: [Community forum](https://github.com/BruhTes/telegram-medical-data-pipeline/discussions)

## 🎉 Project Status

**✅ ALL TASKS COMPLETE - PRODUCTION READY!**

This project represents a complete, production-ready data pipeline for Ethiopian medical business analytics. All components are implemented, tested, and integrated for automated operation.

---

**Built with ❤️ for Ethiopian Medical Business Analytics**
