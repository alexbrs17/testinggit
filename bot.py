import sys
import psycopg2

import pyfiglet
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

from handlers.close_ticket_handler import (
    close_command,
    close_category_callback,
    close_notes_handler,
    close_mention_handler,
)
from handlers.kpi_handler import kpi_command
from handlers.ai_assistant_handler import ai_command, ai_off_command, group_ai_handler
from handlers.usage_stats_handler import usage_stats_command
from handlers.ticket_handler import ticket_detail
from utils.config import TELEGRAM_BOT_TOKEN, DB_URL
from utils.logger import setup_logger
from handlers.start_handler import help_command, start
from handlers.echo_handler import echo
from handlers.import_db_handler import import_db_handler
from handlers.user_management_handler import (
    handle_choose_role_callback,
    handle_ignore_user_callback,
    handle_register_as_admin_callback,
    handle_register_as_guest_callback,
    handle_register_as_pic_callback,
    handle_register_nop_callback,
    new_user_command,
    register_command,
    edit_user_command,
    delete_user_command,
    list_user_command,
)
from handlers.sync_handler import sync_command
from handlers.dashboard_handler import dashboard_command, exportdashboard_command
from handlers.summary_handler import summary_handler
from handlers.summary_weekly_handler import summary_weekly_command
from handlers.summary_ticket_handler import summary_ticket_command
from handlers.report_weekly_handler import report_weekly_command
from handlers.list_ticket_handler import list_handler
from handlers.group_handler import get_group_id_command
from handlers.unknown_handler import unknown_command
from jobs.scheduler import (
    run_scheduler_command,
    check_scheduled_commands,
    stop_scheduler_command,
    test_reminder_command,
    test_summary_broadcast_command,
    test_poi_alert_command,
    test_stolen_alert_command,
    ensure_scheduler_running,
)

logger = setup_logger(__name__)


def check_connection():
    try:
        logger.info("Checking database connection...")
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema = 'SQA_SUMBAGUT';
        """)
        cur.fetchall()
        cur.close()
        conn.close()
        logger.info("Database connection OK and tables verified.")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


async def _on_startup(app: Application) -> None:
    """Auto-start the daily scheduler so it doesn't require a manual
    /runscheduler after every restart/redeploy (it used to silently drop
    whenever the container restarted)."""
    logger.info("Bot identity: @%s (id %s)", app.bot.username, app.bot.id)
    started = ensure_scheduler_running(app.job_queue, app.bot_data)
    if started:
        logger.info("Daily scheduler auto-started on boot.")
    else:
        logger.info("Daily scheduler already running, skipped auto-start.")
        #this is just for testing


def main():
    logger.info("Initializing Telegram bot...")

    # Check DB once on startup
    if not check_connection():
        logger.error("Bot will not start because database connection failed.")
        sys.exit(1)

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .pool_timeout(30.0)
        .post_init(_on_startup)
        .build()
    )

    # Core commands
    app.add_handler(CommandHandler("start", start))
    # app.add_handler(CommandHandler("register", register_command))
    app.add_handler(CommandHandler("register", new_user_command))
    app.add_handler(CommandHandler("edituser", edit_user_command))
    app.add_handler(CommandHandler("deleteuser", delete_user_command))
    app.add_handler(CommandHandler("listuser", list_user_command))
    app.add_handler(CommandHandler("groupid", get_group_id_command))
    app.add_handler(CommandHandler("help", help_command))

    # Business commands
    app.add_handler(CommandHandler("sync", sync_command))
    app.add_handler(CommandHandler("summary_regional", summary_handler))
    app.add_handler(CommandHandler("summaryweekly", summary_weekly_command))
    app.add_handler(CommandHandler("summaryticket", summary_ticket_command))
    app.add_handler(CommandHandler("reportweekly", report_weekly_command))
    app.add_handler(CommandHandler("list_nop", list_handler))
    app.add_handler(CommandHandler("close", close_command))
    app.add_handler(CommandHandler("kpi", kpi_command))
    app.add_handler(CommandHandler("ai", ai_command))
    app.add_handler(CommandHandler("usagestats", usage_stats_command))
    app.add_handler(CommandHandler("aioff", ai_off_command))
    app.add_handler(CommandHandler("dashboard", dashboard_command))
    app.add_handler(CommandHandler("exportdashboard", exportdashboard_command))
    app.add_handler(CommandHandler("ticket_info", ticket_detail))

    # Import DB
    app.add_handler(CommandHandler("importdb", import_db_handler))
    app.add_handler(MessageHandler(filters.Document.ALL & filters.CaptionRegex("^/importdb"), import_db_handler))

    # Close ticket — category callback + notes reply
    app.add_handler(CallbackQueryHandler(close_category_callback, pattern="^close_cat:"))
    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY & ~filters.COMMAND, close_notes_handler))
    # Group -1 supaya jalan terpisah dari handler teks di group 0 (yang berhenti di match pertama)
    app.add_handler(
        MessageHandler(filters.ChatType.GROUPS & filters.TEXT & ~filters.COMMAND, close_mention_handler),
        group=-1,
    )
    # Group sendiri (-2), kalau sama -1 handler close menelan semua teks group dan AI tidak pernah jalan
    app.add_handler(
        MessageHandler(filters.ChatType.GROUPS & filters.TEXT & ~filters.COMMAND, group_ai_handler),
        group=-2,
    )

    # CallbackQuery Handlers
    app.add_handler(CallbackQueryHandler(handle_choose_role_callback, pattern="^choose_role$"))
    app.add_handler(CallbackQueryHandler(handle_register_as_admin_callback, pattern="^register_as_admin$"))
    app.add_handler(CallbackQueryHandler(handle_register_as_guest_callback, pattern="^register_as_guest$"))
    app.add_handler(CallbackQueryHandler(handle_register_as_pic_callback, pattern="^register_as_pic$")) 
    app.add_handler(CallbackQueryHandler(handle_register_nop_callback, pattern="^register_nop_"))
    app.add_handler(CallbackQueryHandler(handle_ignore_user_callback, pattern="^ignore_user"))

    # Scheduler commands
    app.add_handler(CommandHandler("runscheduler", run_scheduler_command))
    app.add_handler(CommandHandler("checkscheduler", check_scheduled_commands))
    app.add_handler(CommandHandler("stopscheduler", stop_scheduler_command))
    app.add_handler(CommandHandler("testreminder", test_reminder_command))
    app.add_handler(CommandHandler("testsummarybroadcast", test_summary_broadcast_command))
    app.add_handler(CommandHandler("testpoialert", test_poi_alert_command))
    app.add_handler(CommandHandler("teststolenalert", test_stolen_alert_command))

    # Fallback echo
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    try:
        print(pyfiglet.figlet_format("NOVLI BOT"))
        logger.info("Bot started")
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        logger.info("Bot stopped")


if __name__ == "__main__":
    main()