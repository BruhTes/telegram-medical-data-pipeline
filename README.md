# Telegram Medical Data Pipeline

End-to-end data pipeline for Telegram medical data analysis using dbt, Dagster, YOLOv8, and FastAPI.

## Overview

This project implements a complete ELT (Extract, Load, Transform) pipeline for analyzing medical business data from Telegram channels. The pipeline includes:

- **Data Extraction**: Telegram message and media scraping
- **Data Storage**: PostgreSQL data warehouse with star schema
- **Data Transformation**: dbt for cleaning and modeling
- **Data Enrichment**: YOLOv8 object detection on images
- **Orchestration**: Dagster for pipeline management
- **Analytics API**: FastAPI for exposing insights

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram      │    │   PostgreSQL    │    │   FastAPI       │
│   Channels      │───▶│   Data          │───▶│   Analytics     │
│                 │    │   Warehouse     │    │   API           │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   dbt           │
                       │   Transformations│
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   YOLOv8        │
                       │   Object        │
                       │   Detection     │
                       └─────────────────┘
```

## Features

- **Real-time Data Collection**: Automated Telegram channel monitoring
- **Data Quality**: Comprehensive data cleaning and validation
- **Scalable Architecture**: Containerized with Docker
- **Analytics Ready**: Optimized star schema for business intelligence
- **AI-Powered Insights**: Object detection for medical product identification
- **RESTful API**: Easy integration with frontend applications

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Telegram API credentials

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/BruhTes/telegram-medical-data-pipeline.git
   cd telegram-medical-data-pipeline
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Telegram API credentials
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the services**
   - FastAPI: http://localhost:8000
   - Dagster: http://localhost:3000
   - PostgreSQL: localhost:5432

## Project Structure

```
telegram-medical-data-pipeline/
├── app/                    # FastAPI application
│   ├── api/               # API endpoints
│   ├── core/              # Core configuration
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── data/                  # Data storage
│   ├── raw/              # Raw data from Telegram
│   ├── processed/        # Cleaned data
│   └── enriched/         # YOLO processed data
├── dbt/                  # dbt transformations
│   ├── models/           # Data models
│   ├── seeds/            # Static data
│   └── tests/            # Data tests
├── dagster/              # Dagster pipelines
├── logs/                 # Application logs
├── requirements.txt       # Python dependencies
├── Dockerfile            # Application container
├── docker-compose.yml    # Service orchestration
└── init.sql             # Database initialization
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_API_ID` | Telegram API ID | Yes |
| `TELEGRAM_API_HASH` | Telegram API Hash | Yes |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | Yes |
| `TELEGRAM_PHONE` | Phone number with country code | Yes |
| `POSTGRES_DB` | Database name | No (default: telegram_medical) |
| `POSTGRES_USER` | Database user | No (default: postgres) |
| `POSTGRES_PASSWORD` | Database password | Yes |

## API Endpoints

### Health Check
- `GET /health` - Service health status

### Analytics
- `GET /analytics/daily-stats` - Daily statistics
- `GET /analytics/top-products` - Top mentioned products
- `GET /analytics/channel-trends` - Channel posting trends
- `GET /analytics/price-analysis` - Price variation analysis

### Data Management
- `POST /data/refresh` - Trigger data refresh
- `GET /data/status` - Pipeline status

## Development

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up database**
   ```bash
   # Start PostgreSQL
   docker-compose up postgres -d
   
   # Run migrations
   psql -h localhost -U postgres -d telegram_medical -f init.sql
   ```

3. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

### Testing

```bash
pytest tests/
```

### Code Quality

```bash
black app/
flake8 app/
mypy app/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support, please open an issue on GitHub.
