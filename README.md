# The Concurrent Contractor™ Telegram Bot

Automated content pipeline bot that captures story ideas via Telegram and manages them in Airtable following the Concurrent Contractor™ Content Management Protocol.

## Features

- 📝 **Story Capture**: Send any text message to capture content ideas
- 🎯 **Framework Classification**: Categorise into Concurrent Contractor™, OPERATE™, or CHAOS frameworks  
- 📚 **Module Assignment**: Organise by Mindset, Motive, Market, Manage, Launchpad
- 🆔 **Auto Content ID**: Sequential assignment following CC[Number] format
- 📊 **Airtable Integration**: Direct creation in Story Pipeline Management table
- ⚡ **Real-time Processing**: Instant categorisation and filing

## Commands

- `/start` - Welcome message and overview
- `/help` - Detailed usage instructions  
- `/frameworks` - View all available frameworks and modules
- `/status` - Check bot status and statistics

## Deployment

Deployed on Railway with automatic GitHub integration. Environment variables configured for secure token management.

## Usage

1. Message the bot with any content idea
2. Select framework using interactive buttons
3. Choose appropriate module/category
4. Pick content type (worksheet, email, etc.)
5. Bot automatically creates Airtable entry with proper Content ID

## Content Management Protocol

Follows The Concurrent Contractor™ Content Management Protocol:
- Unique Content ID system: CC[Sequential Number][Type Code]
- Framework integration across all content types
- Status progression: Telegram Input → In Development → Complete → FINAL
- Version control starting at v1.0
- Complete metadata tracking

## Architecture

- **Python**: Async bot implementation
- **Telegram Bot API**: User interface and interaction
- **Airtable API**: Database integration and content management
- **Railway**: Cloud deployment and hosting
- **GitHub**: Version control and continuous deployment
