"""
Configuration centralisée de l'application Fire Snake 301
"""

# Version de l'application
APP_VERSION = "1.2.0"
APP_NAME = "Fire Snake 301"
APP_DESCRIPTION = "Générateur de redirections 301 avec IA"

# Info de déploiement
DEPLOYMENT_ENV = "production"  # ou "development" selon l'environnement

# Métadonnées pour l'interface
APP_METADATA = {
    "version": APP_VERSION,
    "team": "Fire Salamander Team",
    "company": "SEPTEO Digital Services",
    "features": [
        "IA sémantique GPT-3.5",
        "Support multilangue",
        "Input universel (XML/JSON/CSV/Text)",
        "Headers HTTP intelligents",
        "Retry avec backoff exponentiel",
        "Filtrage des médias",
        "Nettoyage d'URLs",
        "Contournement Cloudflare"
    ]
}