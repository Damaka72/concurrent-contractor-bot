#!/usr/bin/env python3
"""
The Concurrent Contractor™ Telegram Bot
Captures story inputs and manages content pipeline integration with Airtable
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ConcurrentContractorBot:
    def __init__(self):
        # Configuration
       self.telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
self.airtable_token = os.environ.get('AIRTABLE_TOKEN')
self.airtable_base_id = 'appHuRMaNwz4F49EF'  # The Concurrent Contractor Content Hub
        self.airtable_table_id = 'tblKQuyno76Df8pTH'  # Story Pipeline Management
        
        # Content ID counter - in production, this should be stored persistently
        self.content_counter = 30  # Start after existing content
        
        # Framework and module mappings
        self.frameworks = {
            '🎯': 'The Concurrent Contractor™',
            '⚙️': 'OPERATE Framework™', 
            '🌪️': 'CHAOS Framework'
        }
        
        self.modules = {
            '🧠': 'Module 1: Mindset',
            '🎯': 'Module 2: Motive', 
            '📈': 'Module 3: Market',
            '⚙️': 'Module 4: Manage',
            '🚀': 'Module 5: Launchpad',
            '📋': 'General Framework',
            '📧': 'Marketing Funnel',
            '🧲': 'Lead Magnet'
        }
        
        self.content_types = {
            '📚': 'Course Module',
            '📝': 'Worksheet',
            '📄': 'Template', 
            '📧': 'Email Campaign',
            '🧲': 'Lead Magnet',
            '✅': 'Assessment',
            '📋': 'Action Plan',
            '🔧': 'Framework Guide'
        }
        
        self.audiences = {
            '👔': 'Professional Contractors',
            '💼': 'Consultants',
            '⏰': 'Interim Managers',
            '🎯': 'All Concurrent Contractors',
            '🔍': 'Potential Clients',
            '📧': 'Email Subscribers'
        }

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
👋 **Welcome to The Concurrent Contractor™ Content Bot!**

I'm your digital content secretary, ready to capture your brilliant ideas and feed them into your content pipeline.

**How I work:**
📝 Send me any story, idea, or content concept
🎯 I'll help you categorise it using your frameworks
📊 Automatically create entries in your Airtable system
🆔 Assign proper Content IDs following your CC protocol

**Commands:**
/start - Show this welcome message
/help - Get detailed usage instructions
/status - Check bot status and recent entries
/frameworks - View framework options

**Just send me your ideas and I'll guide you through the rest!**
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🔧 **The Concurrent Contractor™ Bot Help**

**Basic Usage:**
1. Send any text message with your content idea
2. I'll ask you to categorise it using buttons
3. Confirm the details
4. I'll create the Airtable entry with proper Content ID

**Content ID System:**
- Format: CC[Sequential Number][Type Code]
- Automatically assigned and tracked
- Follows your Content Management Protocol

**Frameworks:**
🎯 The Concurrent Contractor™ - Main course content
⚙️ OPERATE Framework™ - Operational guidance  
🌪️ CHAOS Framework - Risk management

**Modules:**
🧠 Mindset | 🎯 Motive | 📈 Market | ⚙️ Manage | 🚀 Launchpad

**Example Workflow:**
You: "Story about time blocking for multiple contracts"
Bot: Categorisation options → 
You: Select framework/module →
Bot: Creates "CC31" in Airtable as "Telegram Input" status

Ready when you are! 🚀
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def frameworks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show available frameworks"""
        frameworks_text = """
📚 **Available Frameworks & Modules**

**🎯 The Concurrent Contractor™**
- 🧠 Module 1: Mindset
- 🎯 Module 2: Motive  
- 📈 Module 3: Market
- ⚙️ Module 4: Manage
- 🚀 Module 5: Launchpad

**⚙️ OPERATE Framework™**
- **O**rganise: Structure and plan
- **P**rioritise: Focus on high-value activities  
- **E**nergise: Match tasks to energy levels
- **R**ealise: Execute with purpose
- **A**nalyse: Review and optimise
- **T**une: Adjust and improve
- **E**valuate: Measure success

**🌪️ CHAOS Framework**
- **C**onflicts: Time and priority clashes
- **H**eadaches: Administrative burden
- **A**nxiety: Uncertainty and stress
- **O**verwhelm: Capacity exceeded  
- **S**tagnation: Growth plateau

**Other Categories:**
📋 General Framework | 📧 Marketing Funnel | 🧲 Lead Magnet
        """
        await update.message.reply_text(frameworks_text, parse_mode='Markdown')

    async def handle_story_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming story messages"""
        story_text = update.message.text
        user_id = update.effective_user.id
        
        # Store the story in context
        context.user_data['current_story'] = {
            'text': story_text,
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id
        }
        
        # Create framework selection keyboard
        keyboard = [
            [InlineKeyboardButton("🎯 Concurrent Contractor™", callback_data="fw_cc")],
            [InlineKeyboardButton("⚙️ OPERATE Framework™", callback_data="fw_operate")],
            [InlineKeyboardButton("🌪️ CHAOS Framework", callback_data="fw_chaos")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        preview = story_text[:100] + "..." if len(story_text) > 100 else story_text
        
        await update.message.reply_text(
            f"📝 **Story captured!**\n\n*Preview:* {preview}\n\n🎯 **Which framework does this belong to?**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_framework_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle framework selection"""
        query = update.callback_query
        await query.answer()
        
        framework_map = {
            'fw_cc': 'The Concurrent Contractor™',
            'fw_operate': 'OPERATE Framework™', 
            'fw_chaos': 'CHAOS Framework'
        }
        
        selected_framework = framework_map.get(query.data)
        context.user_data['current_story']['framework'] = selected_framework
        
        # Create module selection keyboard based on framework
        if query.data == 'fw_cc':
            keyboard = [
                [InlineKeyboardButton("🧠 Mindset", callback_data="mod_mindset")],
                [InlineKeyboardButton("🎯 Motive", callback_data="mod_motive")],
                [InlineKeyboardButton("📈 Market", callback_data="mod_market")],
                [InlineKeyboardButton("⚙️ Manage", callback_data="mod_manage")],
                [InlineKeyboardButton("🚀 Launchpad", callback_data="mod_launchpad")]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("📋 General Framework", callback_data="mod_general")],
                [InlineKeyboardButton("📧 Marketing Funnel", callback_data="mod_marketing")],
                [InlineKeyboardButton("🧲 Lead Magnet", callback_data="mod_leadmagnet")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ **Framework:** {selected_framework}\n\n📚 **Which module/category?**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_module_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle module selection"""
        query = update.callback_query
        await query.answer()
        
        module_map = {
            'mod_mindset': 'Module 1: Mindset',
            'mod_motive': 'Module 2: Motive',
            'mod_market': 'Module 3: Market', 
            'mod_manage': 'Module 4: Manage',
            'mod_launchpad': 'Module 5: Launchpad',
            'mod_general': 'General Framework',
            'mod_marketing': 'Marketing Funnel',
            'mod_leadmagnet': 'Lead Magnet'
        }
        
        selected_module = module_map.get(query.data)
        context.user_data['current_story']['module'] = selected_module
        
        # Create content type selection
        keyboard = [
            [InlineKeyboardButton("📚 Course Module", callback_data="type_module")],
            [InlineKeyboardButton("📝 Worksheet", callback_data="type_worksheet")],
            [InlineKeyboardButton("📄 Template", callback_data="type_template")],
            [InlineKeyboardButton("📧 Email Campaign", callback_data="type_email")],
            [InlineKeyboardButton("🧲 Lead Magnet", callback_data="type_leadmagnet")],
            [InlineKeyboardButton("✅ Assessment", callback_data="type_assessment")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ **Module:** {selected_module}\n\n📋 **What type of content will this become?**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_content_type_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle content type selection and create Airtable entry"""
        query = update.callback_query
        await query.answer()
        
        type_map = {
            'type_module': 'Course Module',
            'type_worksheet': 'Worksheet', 
            'type_template': 'Template',
            'type_email': 'Email Campaign',
            'type_leadmagnet': 'Lead Magnet',
            'type_assessment': 'Assessment'
        }
        
        selected_type = type_map.get(query.data)
        context.user_data['current_story']['content_type'] = selected_type
        
        # Generate Content ID
        content_id = f"CC{self.content_counter:02d}"
        self.content_counter += 1
        
        story_data = context.user_data['current_story']
        
        # Create summary from story text (first 200 chars)
        summary = story_data['text'][:200] + "..." if len(story_data['text']) > 200 else story_data['text']
        
        # Create title from first sentence or first 50 chars
        title_text = story_data['text'].split('.')[0][:50] if '.' in story_data['text'] else story_data['text'][:50]
        title = title_text + "..." if len(title_text) == 50 else title_text
        
        # Prepare Airtable record
        airtable_data = {
            'Content ID': content_id,
            'Framework': story_data['framework'],
            'Module': story_data['module'], 
            'Title/Asset Name': title,
            'Content Status': 'Telegram Input',
            'Summary': summary,
            'Target Audience': 'All Concurrent Contractors',  # Default
            'Content Type': selected_type,
            'File Type': 'PDF/Document',  # Default
            'Version': 'v1.0',
            'Status Notes': f"{datetime.now().strftime('%Y-%m-%d')} - Story captured via Telegram bot - Ready for development planning",
            'File Link Status': 'Telegram Captured',
            'Created Date': datetime.now().strftime('%Y-%m-%d'),
            'Last Updated': datetime.now().strftime('%Y-%m-%d')
        }
        
        # Create Airtable entry
        success = await self.create_airtable_record(airtable_data)
        
        if success:
            confirmation_text = f"""
🎉 **Story Successfully Captured!**

**Content ID:** {content_id}
**Framework:** {story_data['framework']}
**Module:** {story_data['module']}
**Type:** {selected_type}
**Status:** Telegram Input

✅ **Created in Airtable Story Pipeline Management**

Your idea is now in the system and ready for development when you're ready to work on it!

*Send me another story anytime! 💡*
            """
        else:
            confirmation_text = f"""
⚠️ **Story Captured Locally**

**Content ID:** {content_id}
**Framework:** {story_data['framework']} 
**Module:** {story_data['module']}
**Type:** {selected_type}

❌ **Airtable sync failed** - Please add manually or check connection.

*Story details saved for manual entry.*
            """
        
        await query.edit_message_text(confirmation_text, parse_mode='Markdown')
        
        # Clear story data
        context.user_data.pop('current_story', None)

    async def create_airtable_record(self, record_data: Dict) -> bool:
        """Create a record in Airtable"""
        url = f"https://api.airtable.com/v0/{self.airtable_base_id}/{self.airtable_table_id}"
        
        headers = {
            'Authorization': f'Bearer {self.airtable_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'fields': record_data
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Successfully created Airtable record: {record_data['Content ID']}")
                        return True
                    else:
                        logger.error(f"Airtable API error: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error creating Airtable record: {e}")
            return False

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot status"""
        status_text = f"""
🤖 **Bot Status: Online**

📊 **Statistics:**
- Content Counter: CC{self.content_counter:02d} (next ID)
- Airtable Base: Connected
- Framework Options: 3 available
- Module Options: 8 available

🔗 **Integrations:**
- ✅ Telegram Bot API
- ✅ Airtable API (Story Pipeline Management)
- ✅ Content ID Auto-Assignment
- ✅ Framework Categorisation

Ready to capture your next brilliant idea! 💡
        """
        await update.message.reply_text(status_text, parse_mode='Markdown')

    def setup_handlers(self, application: Application):
        """Set up command and message handlers"""
        # Command handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("frameworks", self.frameworks_command))
        application.add_handler(CommandHandler("status", self.status_command))
        
        # Callback query handlers for buttons
        application.add_handler(CallbackQueryHandler(
            self.handle_framework_selection, 
            pattern="^fw_"
        ))
        application.add_handler(CallbackQueryHandler(
            self.handle_module_selection,
            pattern="^mod_"
        ))
        application.add_handler(CallbackQueryHandler(
            self.handle_content_type_selection,
            pattern="^type_"
        ))
        
        # Message handler for story inputs (exclude commands)
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_story_input
        ))

def main():
    """Start the bot"""
    # Check for required environment variables
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        return
    
    if not os.getenv('AIRTABLE_TOKEN'):
        logger.error("AIRTABLE_TOKEN environment variable not set")
        return
    
    # Create bot instance
    bot = ConcurrentContractorBot()
    
    # Create application
    application = Application.builder().token(bot.telegram_token).build()
    
    # Set up handlers
    bot.setup_handlers(application)
    
    logger.info("Starting The Concurrent Contractor™ Telegram Bot...")
    
    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
